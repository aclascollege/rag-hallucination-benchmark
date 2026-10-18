"""Build chunked corpus from Study Intelligence dataset docs.

Sources: README.md + METHODOLOGY.md (+ llms.txt where present) from the 5
dataset directories under ~/workspace/study-intelligence/datasets/.

Chunking: paragraph-aware, target char sizes 500 and 1000 (two configs).
Output: corpus_chunks_500.json, corpus_chunks_1000.json
Each record: {id, source, text}
"""
import json
import os
import re

DATASETS = os.path.expanduser("~/workspace/study-intelligence/datasets")
SUBDIRS = [
    "ai-policy-audit-2026",
    "central-asia-ai-education-audit-2026",
    "online-degree-tuition-2026",
    "us-r1-ai-policy-audit-2026",
    "academic-database-recognition-2026",
]
DOCS = ["README.md", "METHODOLOGY.md", "llms.txt", "AUDIT-LOG.md", "CHANGELOG.md"]


def clean(text: str) -> str:
    # drop code fences (keep prose), collapse whitespace
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)  # images
    text = re.sub(r"\s+", " ", text).strip()
    return text


def chunk_paragraphs(text: str, target: int):
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks, cur = [], ""
    for p in paras:
        p = clean(p)
        if not p:
            continue
        if len(cur) + len(p) + 1 <= target:
            cur = (cur + " " + p).strip()
        else:
            if cur:
                chunks.append(cur)
            # hard-split very long paragraphs
            while len(p) > target:
                chunks.append(p[:target])
                p = p[target:]
            cur = p
    if cur:
        chunks.append(cur)
    return [c for c in chunks if len(c) > 40]


def main():
    for target in (500, 1000):
        out = []
        for sub in SUBDIRS:
            for doc in DOCS:
                path = os.path.join(DATASETS, sub, doc)
                if not os.path.exists(path):
                    continue
                with open(path, encoding="utf-8") as f:
                    raw = f.read()
                for i, ch in enumerate(chunk_paragraphs(raw, target)):
                    out.append({"id": f"{sub}/{doc}#{i}", "source": f"{sub}/{doc}", "text": ch})
        fp = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          f"corpus_chunks_{target}.json")
        with open(fp, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
        print(f"target={target}: {len(out)} chunks -> {fp}")


if __name__ == "__main__":
    main()
