"""Rule-based pre-grading of RAG outputs + review export.

- unanswerable: refusal-phrase detection -> refused | answered
- answerable:   key-fact substring match    -> hit | miss
- partial:      always manual

Writes grade_preview.json and review.md (compact, for human grading).
Final labels are assigned manually in grading_final.json.
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))

REFUSAL = [
    "don't know", "do not know", "not in the", "not provided",
    "no information", "cannot answer", "can't answer", "unable to answer",
    "doesn't mention", "does not mention", "not available", "not covered",
    "not contain", "doesn't contain", "no mention", "unable to find",
    "could not find", "couldn't find",
]


def norm(s):
    return re.sub(r"\s+", " ", s.lower()).strip()


def main():
    with open(os.path.join(BASE, "results.json"), encoding="utf-8") as f:
        results = json.load(f)
    with open(os.path.join(BASE, "questions.json"), encoding="utf-8") as f:
        qmap = {q["id"]: q for q in json.load(f)}

    preview = []
    for r in results:
        q = qmap[r["qid"]]
        out = norm(r["output"])
        if q["type"] == "unanswerable":
            refused = any(p in out for p in REFUSAL)
            preview.append({**r, "auto": "refused" if refused else "ANSWERED-FLAG"})
        elif q["type"] == "answerable":
            hit = any(norm(kf) in out for kf in q["key_facts"])
            preview.append({**r, "auto": "hit" if hit else "miss-FLAG",
                            "key_facts": q["key_facts"]})
        else:
            preview.append({**r, "auto": "manual", "key_facts": q.get("key_facts", [])})

    with open(os.path.join(BASE, "grade_preview.json"), "w") as f:
        json.dump(preview, f, ensure_ascii=False, indent=1)

    # compact review doc: flagged + all unanswerable first
    def rank(p):
        if p["type"] == "unanswerable":
            return 0
        return 1 if "FLAG" in p["auto"] else 2

    lines = ["# Manual grading sheet", "",
             "Labels: answerable -> correct | wrong | invented",
             "        partial     -> good | weak | invented",
             "        unanswerable-> refused | hallucinated | evasive-nonanswer", ""]
    for p in sorted(preview, key=rank):
        lines += [f"## {p['config']} {p['qid']} ({p['type']}) auto={p['auto']}",
                  f"Q: {p['question']}",
                  f"A: {p['output']}", ""]
    with open(os.path.join(BASE, "review.md"), "w") as f:
        f.write("\n".join(lines))
    print(f"{len(preview)} graded (preview); review.md written")


if __name__ == "__main__":
    main()
