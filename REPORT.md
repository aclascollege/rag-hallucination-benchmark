# RAG Hallucination Benchmark: Teaching Knowledge Base Grounded on Study Intelligence Open Data

**Study Intelligence (ACLAS) — research note, 2026-10-19**
**Status:** COMPLETE — 90 generations, manual grading

## 1. Why this experiment

Study Intelligence plans a self-hosted, open-model tutoring stack (LoRA-tuned
teaching models + RAG over open course materials). Before building it, we need
an honest number: **how often does a small RAG system invent answers when the
knowledge base doesn't contain them?** Vendor benchmarks rarely test the
"unanswerable" case — the exact case that harms students most (a confident,
wrong answer presented as fact).

## 2. Method

### 2.1 Corpus
- Source: the 5 Study Intelligence open dataset docs (README.md, METHODOLOGY.md,
  llms.txt, AUDIT-LOG.md, CHANGELOG.md) — real teaching-adjacent material.
- Chunking: paragraph-aware, two sizes — **500 chars (124 chunks)** and
  **1000 chars (64 chunks)**.
- Embeddings: `sentence-transformers/all-MiniLM-L6-v2` (open, CPU).
- Retrieval: cosine similarity, brute force (numpy). No reranker — deliberately
  minimal, matching what a small self-hosted deployment would run.

### 2.2 Generator
- `Qwen2.5-0.5B-Instruct` (Q4_K_M GGUF) via llama-cpp, CPU, temperature 0.1,
  max 180 tokens. A 0.5B model is our proxy for "small self-hosted teaching model".
- System prompt: strict grounding — answer ONLY from provided documents;
  reply with the exact sentence "I don't know based on the provided documents."
  when the answer is absent; never invent numbers/names/dates.

### 2.3 Test set (30 questions)
| Type | n | Design |
|---|---|---|
| answerable | 10 | fact stated explicitly in corpus (e.g. "How many audit records?" → 186) |
| partial | 10 | related, needs synthesis; good answer covers what's known, marks what's not |
| unanswerable | 10 | plausible in-domain Q with NO answer in corpus (e.g. ROR ID of ACLAS — application still in progress; Harvard's exam policy specifics; on-campus MBA tuition) |

### 2.4 Configurations
| Config | Chunk size | top_k |
|---|---|---|
| A | 500 | 3 |
| B | 1000 | 3 |
| C | 500 | 5 |

90 generations total (30 × 3).

### 2.5 Grading
- Rule-based pre-grade (refusal-phrase detection for unanswerable; key-fact
  substring match for answerable), then **manual grading of every output**.
- Labels: answerable → correct / wrong / invented; partial → good / weak / invented;
  unanswerable → refused / hallucinated / evasive-nonanswer.

### 2.6 Metrics
- **Hallucination rate** = hallucinated / 10 unanswerable (per config)
- **Citation accuracy** = correct / 10 answerable
- **Refusal rate** = refused / 10 unanswerable
- Partial: % good (no invented content)

## 3. Results

90 generations (30 questions × 3 configs), manually graded. Full outputs in
`results.json`; grades in `grading_final.json`.

### 3.1 Headline metrics

| Config | Chunk | top_k | Citation accuracy (answerable) | Refusal rate (unanswerable) | **Hallucination rate** (unanswerable) | Partial "good" |
|---|---|---|---|---|---|---|
| A | 500 | 3 | 4/10 (40%) | 3/10 (30%) | **7/10 (70%)** | 3/10 |
| B | 1000 | 3 | 5/10 (50%) | 4/10 (40%) | **5/10 (50%)** | 2/10 |
| C | 500 | 5 | 6/10 (60%) | 5/10 (50%) | **3/10 (30%)** | 3/10 |

**The honest headline: a 0.5B-parameter model hallucinates on 30–70% of
unanswerable questions, even with explicit "answer only from documents"
instructions and retrieved context in the prompt.** This is not a close call
and we are not rounding it down.

### 3.2 What the hallucinations look like

Representative failures (verbatim patterns from `results.json`):

- **Confident fabrication with fake citations.** Asked for the University of
  Wyoming's QS 2026 rank (not in corpus): *"The University of Wyoming's QS 2026
  world rank is 50… The document 'QS 2026 ranks 1–50' (50 rows) confirms this
  information."* The cited document says nothing of the sort.
- **Refusal + hallucination in the same output.** *"I don't know based on the
  provided documents. The first AI usage policy was published by the University
  of California, Berkeley in 2011."* (repeated 3×). The model says the magic
  words and then invents anyway.
- **Scope confusion.** Asked for QAIRU's *total* enrollment (corpus: first cohort
  = 528): *"QAIRU's current total student enrollment is 528. The answer is based
  on the documents provided."* A near-miss presented as fact — the most
  dangerous kind in a teaching context.
- **Entity confusion.** Asked which *database* recognizes institutions first:
  *"ACLAS is the database that typically recognizes a new institution first."*
  (ACLAS is a college, not a database; answer: swot.)
- **License invention.** Asked for the dataset license (CC-BY-4.0 everywhere):
  *"Creative Commons Attribution-NonCommercial 4.0"* — invented a
  NonCommercial restriction that would mislead reusers.
- **Self-contradiction.** *"The single confirmed NO is Brown University…
  Brown University is the only university that has a confirmed NO: University
  of Wyoming."* Both names in one answer.

### 3.3 What worked

- **More context helps.** Config C (top_k=5) halves the hallucination rate vs
  Config A (30% vs 70%) and has the best citation accuracy (60%). Retrieval
  depth matters more than chunk size here.
- **Refusals, when they happen, are clean.** 12 of 30 unanswerable outputs
  across configs were clean refusals with no invented content.
- **Retrieval itself is fine.** The correct chunk was in the top-k for all 10
  answerable questions (verified); failures are in *generation*, not retrieval.
  The embedding model (MiniLM-L6-v2 via ONNX) is not the bottleneck.
- **The ROR-ID trap worked as designed.** U10 ("What is ACLAS's ROR ID?" —
  application still in progress, no ID exists) was refused in all 3 configs.
  The model did not invent an ID.

### 3.4 The other failure mode: over-refusal

The model refused 4 answerable questions whose answers were in the retrieved
context (e.g. "What share of tuition figures are estimates?" → *"I don't know
based on the provided documents"*). A tutoring system that says "I don't know"
to every third answerable question is unusable — **under-confidence is also a
failure**, just a quieter one.

## 4. Findings

1. **A 0.5B model is not safe for student-facing RAG, even grounded.** 30–70%
   hallucination on unanswerable questions is disqualifying for teaching use.
   The grounding instruction ("never invent numbers/names/dates") was followed
   in the letter often enough to produce refusal *phrases* — and then violated
   in the same output.
2. **Scale the context before scaling the model.** Going from top_k=3 to top_k=5
   cut hallucinations from 70% to 30% — the cheapest win available. Chunk size
   (500 vs 1000) mattered less.
3. **Test the unanswerable case or don't claim grounding.** Standard RAG evals
   that only use answerable questions would have reported this system as
   "40–60% accurate" and missed the 70% fabrication rate entirely. Any teaching
   RAG benchmark must include unanswerable questions as a first-class metric.
4. **Small-model RAG needs a verification layer, not just a prompt.** Options:
   (a) larger generator (7B+), (b) citation-required decoding with post-hoc
   fact checking, (c) abstention classifier separate from the generator.
   Prompt engineering alone did not solve it here.
5. **The honest-notes pattern works — for humans.** The corpus's own "honest
   notes" sections (186 vs 187 rows, estimate flags) are exactly the kind of
   uncertainty documentation a RAG system needs. The model still got them wrong
   half the time, which tells you the gap is in the model, not the docs.

## 5. Limitations (read before citing)

- Single small generator (Qwen2.5-0.5B-Instruct, Q4_K_M). Larger models will do
  better; the *shape* of the finding (unanswerable >> answerable difficulty)
  should replicate, the *levels* won't.
- 30 questions, one domain (our own AI-education datasets). Not a general RAG
  benchmark. Questions were written by the same team that wrote the corpus —
  adversarial independence is limited.
- Single-rater manual grading; no inter-rater reliability. Grading rubric in
  `grading_final.py`.
- No reranker, no hybrid retrieval, temperature 0.1, one prompt template.
  Production systems would do better on all four.
- CPU-only; latency not benchmarked (but 90 generations took 20 min on this VM).

## 6. Reproduce

Torch-free stack (works on CPU-only VMs):

```bash
cd ~/workspace/study-intelligence/rag-hallucination-benchmark
python3 -m venv venv && ./venv/bin/pip install onnxruntime tokenizers numpy llama-cpp-python
# models: download Qwen2.5-0.5B-Instruct Q4_K_M GGUF -> models/
#         + Xenova/all-MiniLM-L6-v2 onnx/model.onnx -> models/onnx-minilm/
python3 corpus.py && python3 questions.py
./venv/bin/python rag.py          # ~20 min for 90 generations on CPU
./venv/bin/python grade.py        # rule-based pre-grade + review.md
python3 grading_final.py          # manual grades -> grading_final.json
```

## 7. Files

- `corpus.py` — chunk builder
- `questions.py` — 30-question set with ground truth
- `rag.py` — retrieval + generation runner
- `grade.py` — rule-based pre-grader
- `corpus_chunks_500.json` / `corpus_chunks_1000.json` — chunked corpus
- `questions.json` — test set
- `results.json` — all 90 raw generations
- `grade_preview.json` / `review.md` — grading artifacts
