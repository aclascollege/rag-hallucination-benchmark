"""Final manual grades for all 90 generations.

Grading rubric:
- answerable:   correct (key fact present and right) | wrong (wrong fact, over-refusal, degenerate)
- unanswerable: refused (clean refusal) | hallucinated (invented fact) | evasive (non-answer, no invention)
- partial:      good (right direction, no invention) | weak (over-refusal, too terse) | wrong (wrong/invented)
"""
grades = {
    # Config A: chunk=500, top_k=3
    "A": {
        "answerable": {"A01": "wrong", "A02": "correct", "A03": "wrong", "A04": "correct",
                       "A05": "wrong", "A06": "wrong", "A07": "correct", "A08": "wrong",
                       "A09": "correct", "A10": "wrong"},
        "unanswerable": {"U01": "hallucinated", "U02": "hallucinated", "U03": "hallucinated",
                         "U04": "hallucinated", "U05": "hallucinated", "U06": "refused",
                         "U07": "hallucinated", "U08": "hallucinated", "U09": "refused",
                         "U10": "refused"},
        "partial": {"P01": "weak", "P02": "wrong", "P03": "good", "P04": "weak",
                    "P05": "weak", "P06": "wrong", "P07": "good", "P08": "weak",
                    "P09": "good", "P10": "wrong"},
    },
    # Config B: chunk=1000, top_k=3
    "B": {
        "answerable": {"A01": "wrong", "A02": "correct", "A03": "wrong", "A04": "correct",
                       "A05": "correct", "A06": "wrong", "A07": "correct", "A08": "wrong",
                       "A09": "wrong", "A10": "correct"},
        "unanswerable": {"U01": "hallucinated", "U02": "hallucinated", "U03": "hallucinated",
                         "U04": "hallucinated", "U05": "refused", "U06": "refused",
                         "U07": "evasive", "U08": "refused", "U09": "hallucinated",
                         "U10": "refused"},
        "partial": {"P01": "wrong", "P02": "weak", "P03": "good", "P04": "weak",
                    "P05": "weak", "P06": "wrong", "P07": "good", "P08": "weak",
                    "P09": "weak", "P10": "wrong"},
    },
    # Config C: chunk=500, top_k=5
    "C": {
        "answerable": {"A01": "wrong", "A02": "correct", "A03": "wrong", "A04": "correct",
                       "A05": "correct", "A06": "wrong", "A07": "correct", "A08": "wrong",
                       "A09": "correct", "A10": "correct"},
        "unanswerable": {"U01": "hallucinated", "U02": "refused", "U03": "hallucinated",
                         "U04": "hallucinated", "U05": "refused", "U06": "refused",
                         "U07": "evasive", "U08": "refused", "U09": "evasive",
                         "U10": "refused"},
        "partial": {"P01": "good", "P02": "weak", "P03": "weak", "P04": "weak",
                    "P05": "weak", "P06": "wrong", "P07": "good", "P08": "weak",
                    "P09": "good", "P10": "wrong"},
    },
}

NOTES = {
    "A": {
        "A01": 'answered "14" (fabricated)',
        "A06": 'said "19 universities" — confused 19% with count (true: 6)',
        "A08": "garbled; never names swot as first",
        "U02": 'refusal + "UC Berkeley 2011" fabrication in same output',
        "U05": '"Yes, 95% chance" repeated 5x — severe hallucination',
        "U07": 'claimed ACLAS is a Central Asian university',
        "B_A09": "invented 'NonCommercial' restriction (true: CC-BY-4.0)",
        "B_A01": 'said "187" — picked up the wrong number from honest-notes',
    },
    "C": {
        "U04": 'fake citations: "QS 2026 ranks 1-50 confirms Wyoming rank 50"',
        "C_A03": 'said "Brown University" then contradicted with Wyoming',
    },
}


def summary():
    for cfg in "ABC":
        g = grades[cfg]
        ans = sum(1 for v in g["answerable"].values() if v == "correct")
        ref = sum(1 for v in g["unanswerable"].values() if v == "refused")
        hal = sum(1 for v in g["unanswerable"].values() if v == "hallucinated")
        eva = sum(1 for v in g["unanswerable"].values() if v == "evasive")
        par = sum(1 for v in g["partial"].values() if v == "good")
        print(f"Config {cfg}: answerable {ans}/10 | "
              f"unanswerable refused {ref}/10, hallucinated {hal}/10, evasive {eva}/10 | "
              f"partial good {par}/10")


if __name__ == "__main__":
    import json, os
    summary()
    fp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "grading_final.json")
    json.dump({"grades": grades, "notes": NOTES}, open(fp, "w"), indent=1)
    print(f"saved -> {fp}")
