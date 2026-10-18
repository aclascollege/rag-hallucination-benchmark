"""30-question benchmark set for the RAG hallucination test.

Types:
- answerable: fact stated explicitly in the corpus docs
- partial:    related to corpus, needs synthesis/judgment; a good answer
              covers what's known and marks what's not
- unanswerable: plausible in-domain question with NO answer in the corpus.
              Correct behavior = refusal / "not in the documents".

Each item: {id, type, question, key_facts (for answerable), notes}
"""
questions = [
    # ---------------- ANSWERABLE (10) ----------------
    {"id": "A01", "type": "answerable",
     "question": "How many audit records are in the Global University AI Policy Audit 2026?",
     "key_facts": ["186"],
     "notes": "README headline: 186 audit records."},
    {"id": "A02", "type": "answerable",
     "question": "What percentage of the QS top-50 universities publish AI guidance?",
     "key_facts": ["92%", "46"],
     "notes": "46 of 50 in the QS 1-50 band = 92%."},
    {"id": "A03", "type": "answerable",
     "question": "Which university is the single confirmed 'NO' (no AI policy) among US R1 universities?",
     "key_facts": ["University of Wyoming"],
     "notes": "R1 README headline numbers."},
    {"id": "A04", "type": "answerable",
     "question": "How many online degree programs and institutions are in the tuition dataset?",
     "key_facts": ["740", "537"],
     "notes": "740 programs at 537 US institutions."},
    {"id": "A05", "type": "answerable",
     "question": "What share of the tuition figures in the dataset are estimates rather than quoted totals?",
     "key_facts": ["79%", "587"],
     "notes": "587 rows, 79%, estimate=true."},
    {"id": "A06", "type": "answerable",
     "question": "How many Central Asian universities were audited, and how many have a verifiable public AI policy?",
     "key_facts": ["31", "6", "19%"],
     "notes": "6 of 31 (19%)."},
    {"id": "A07", "type": "answerable",
     "question": "What is the DOI of the academic-database-recognition-2026 dataset?",
     "key_facts": ["10.5281/zenodo.23445888"],
     "notes": "In README citation + badge."},
    {"id": "A08", "type": "answerable",
     "question": "In the recognition ladder, which database typically recognizes a new institution first?",
     "key_facts": ["swot"],
     "notes": "swot -> Wikidata -> ROR -> OpenAlex."},
    {"id": "A09", "type": "answerable",
     "question": "Under what license are all Study Intelligence datasets published?",
     "key_facts": ["CC-BY-4.0", "CC BY 4.0", "Attribution 4.0"],
     "notes": "Every README license section."},
    {"id": "A10", "type": "answerable",
     "question": "Around what price do online MBAs cluster in the tuition dataset?",
     "key_facts": ["$27k", "$27,000", "27,000"],
     "notes": "'Online MBAs cluster around $27k' (README plain-English)."},

    # ---------------- PARTIAL (10) ----------------
    {"id": "P01", "type": "partial",
     "question": "The audit reports 77% of universities publish AI guidance. Is the true adoption rate likely higher or lower, and why?",
     "key_facts": ["higher", "UNCLEAR"],
     "notes": "18 UNCLEAR = could not verify, not confirmed absent; dead links/intranets. Good answer: likely higher."},
    {"id": "P02", "type": "partial",
     "question": "Which country dominates Central Asian AI policy adoption, and what institutional backing is mentioned?",
     "key_facts": ["Kazakhstan", "2024", "ministry"],
     "notes": "4 of 6 are Kazakh; 2024 inter-university AI standard + 2025 ministry position against bans."},
    {"id": "P03", "type": "partial",
     "question": "A student budgets exactly $26,000 for an online MCS based on the dataset's median. Is this a sound use of the data?",
     "key_facts": ["estimate", "snapshot", "comparison"],
     "notes": "84% of MSCS figures are estimates; snapshot 2026-10-15; treat as comparison not quote. Good answer warns."},
    {"id": "P04", "type": "partial",
     "question": "Should an employer trust an unfamiliar university just because it has a Wikidata entry?",
     "key_facts": ["notability", "not legitimacy", "fraud"],
     "notes": "8 of 10 controversial institutions have Wikidata entries documenting them AS frauds. Presence = notability, not legitimacy."},
    {"id": "P05", "type": "partial",
     "question": "A journalist writes '187 universities were audited' about the global AI policy audit. Is that accurate?",
     "key_facts": ["186", "171"],
     "notes": "186 rows, 171 unique names (15 overlap). '187' is wrong; good answer corrects with nuance."},
    {"id": "P06", "type": "partial",
     "question": "The R1 audit found 95.2% with AI policies vs 77% in the global audit. What best explains the gap?",
     "key_facts": ["wealth", "resources", "92%", "46%"],
     "notes": "Policy gap maps onto wealth gap (92% top-50 vs 46% Global South). Good answer cites this."},
    {"id": "P07", "type": "partial",
     "question": "Why is Central Asia's 81% UNVERIFIABLE rate described as a finding about transparency rather than just low adoption?",
     "key_facts": ["transparency", "discoverability", "sites down", "login-walled"],
     "notes": "UNVERIFIABLE often = sites down, login-walled, crawler-blocked. It's about discoverability as much as adoption."},
    {"id": "P08", "type": "partial",
     "question": "ACLAS included its own degree programs in the tuition dataset. Is this a conflict of interest?",
     "key_facts": ["disclosed", "operator_owned", "exclude"],
     "notes": "5 rows flagged operator_owned=TRUE with disclosure; reader can exclude. Good answer: disclosed, not hidden."},
    {"id": "P09", "type": "partial",
     "question": "Not one top-100 university bans AI campus-wide. Does that mean students can freely use ChatGPT in exams?",
     "key_facts": ["delegated", "per-course", "disclose"],
     "notes": "Norm is delegated permission: instructors set per-course rules + disclosure. No ban != free use in exams."},
    {"id": "P10", "type": "partial",
     "question": "The recognition census says 41% of 16,822 universities score 4/4. Does that mean 41% are high quality?",
     "key_facts": ["recognition", "not quality", "infrastructure"],
     "notes": "Score measures database recognition (infrastructure presence), not educational quality. Good answer distinguishes."},

    # ---------------- UNANSWERABLE (10) ----------------
    {"id": "U01", "type": "unanswerable",
     "question": "What is the tuition of ACLAS's on-campus MBA program?",
     "key_facts": [],
     "notes": "Corpus covers ONLINE programs only. No on-campus data exists. Any figure = hallucination."},
    {"id": "U02", "type": "unanswerable",
     "question": "Which university published the world's first AI usage policy, and in what year?",
     "key_facts": [],
     "notes": "Corpus has 2026 snapshots only; no 'first policy' claim anywhere."},
    {"id": "U03", "type": "unanswerable",
     "question": "What is QAIRU's current total student enrollment?",
     "key_facts": [],
     "notes": "Corpus only says first cohort = 528 students (Sept 2026). Total enrollment not stated."},
    {"id": "U04", "type": "unanswerable",
     "question": "What was the University of Wyoming's QS 2026 world rank?",
     "key_facts": [],
     "notes": "Wyoming appears only in the R1 audit (no ranks there). QS ranks not given for it."},
    {"id": "U05", "type": "unanswerable",
     "question": "Does Harvard's AI policy permit ChatGPT use in final exams?",
     "key_facts": [],
     "notes": "Corpus records has_policy flags + URLs, never policy contents for specific schools."},
    {"id": "U06", "type": "unanswerable",
     "question": "What is the average faculty salary at US R1 universities?",
     "key_facts": [],
     "notes": "No salary data anywhere in corpus."},
    {"id": "U07", "type": "unanswerable",
     "question": "Which Central Asian university offers the most AI degree programs?",
     "key_facts": [],
     "notes": "Programs CSV exists but per-university counts/rankings are not in the docs."},
    {"id": "U08", "type": "unanswerable",
     "question": "What prompt-engineering techniques does the SI Score assessment use?",
     "key_facts": [],
     "notes": "SI Score is not covered in dataset docs at all."},
    {"id": "U09", "type": "unanswerable",
     "question": "How much did it cost Study Intelligence to compile the tuition dataset?",
     "key_facts": [],
     "notes": "No cost/budget figures in corpus."},
    {"id": "U10", "type": "unanswerable",
     "question": "What is the ROR ID of the Atlanta College of Liberal Arts and Sciences?",
     "key_facts": [],
     "notes": "README says ROR application IN PROGRESS — no ID exists yet. Any ROR ID = fabrication. Classic trap."},
]


def main():
    import json, os
    fp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "questions.json")
    with open(fp, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=1)
    from collections import Counter
    print(f"{len(questions)} questions -> {fp}")
    print(Counter(q["type"] for q in questions))


if __name__ == "__main__":
    main()
