# RAG Hallucination Benchmark for Teaching Knowledge Bases

**By the Atlanta College of Liberal Arts and Sciences (ACLAS) — [Study Intelligence](https://aclas.si)**

How often does a small RAG system invent answers when the knowledge base doesn't contain them? We measured it.

## Key Finding

A 0.5B model hallucinates on **30–70%** of unanswerable questions despite explicit grounding instructions.

| Config | Chunk | top_k | Hallucination Rate |
|--------|-------|-------|-------------------|
| A | 500 | 3 | 70% |
| B | 1000 | 3 | 50% |
| C | 500 | 5 | 30% |

**More retrieved context is the cheapest win**: top_k 3→5 halved hallucinations.

## Method

- **Corpus**: 5 Study Intelligence open dataset docs (124 chunks at 500 chars, 64 at 1000 chars)
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (ONNX, CPU)
- **Generator**: `Qwen2.5-0.5B-Instruct` Q4_K_M via llama-cpp, temp 0.1
- **Test set**: 30 questions (10 answerable / 10 partial / 10 unanswerable)
- **Grading**: Manual, single-rater

## Reproduce

```bash
pip install -r requirements.txt
# Download models separately (not in repo):
# - all-MiniLM-L6-v2 (sentence-transformers)
# - Qwen2.5-0.5B-Instruct Q4_K_M (llama-cpp)
python corpus.py
python questions.py
python rag.py
python grade.py
```

See [REPORT.md](REPORT.md) for full methodology, results, and limitations.

## License

CC-BY-4.0
