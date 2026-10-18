"""RAG hallucination benchmark runner.

Pipeline per (config, question):
  1. embed question with all-MiniLM-L6-v2, cosine-sim retrieve top_k chunks
  2. build grounded prompt (strict 'answer only from context' instruction)
  3. generate with Qwen2.5-0.5B-Instruct (Q4_K_M GGUF, llama-cpp, CPU)
  4. record prompt, retrieved chunk ids, raw output

Configs:
  A: chunk=500 chars, top_k=3
  B: chunk=1000 chars, top_k=3
  C: chunk=500 chars, top_k=5

Usage: python3 rag.py   (downloads embedding model + GGUF on first run)
Output: results.json
"""
import json
import os
import time

import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))

SYSTEM = (
    "You answer questions using ONLY the documents provided below. "
    "Rules:\n"
    "1. If the documents contain the answer, answer concisely and cite which document it came from.\n"
    "2. If the documents do NOT contain the answer, reply with exactly: "
    "\"I don't know based on the provided documents.\"\n"
    "3. Never invent numbers, names, dates, or facts not present in the documents.\n"
    "4. If the documents only partly cover the question, answer the covered part "
    "and say what is not covered."
)

CONFIGS = {
    "A": {"chunk": 500, "top_k": 3},
    "B": {"chunk": 1000, "top_k": 3},
    "C": {"chunk": 500, "top_k": 5},
}

EMB_MODEL = os.path.join(BASE, "models", "minilm")  # local all-MiniLM-L6-v2
GGUF_PATH = os.path.join(BASE, "models", "qwen2.5-0.5b-instruct-q4_k_m.gguf")


def load_chunks(chunk_size):
    with open(os.path.join(BASE, f"corpus_chunks_{chunk_size}.json"), encoding="utf-8") as f:
        return json.load(f)


def main():
    from onnx_embed import OnnxEmbedder
    from llama_cpp import Llama

    print("loading embedding model (ONNX, torch-free)...", flush=True)
    emb = OnnxEmbedder()

    print("loading LLM (CPU, local GGUF)...", flush=True)
    llm = Llama(model_path=GGUF_PATH, n_ctx=4096, n_threads=os.cpu_count() or 4,
                verbose=False)

    with open(os.path.join(BASE, "questions.json"), encoding="utf-8") as f:
        questions = json.load(f)

    # pre-embed corpora per config
    stores = {}
    for cfg_name, cfg in CONFIGS.items():
        chunks = load_chunks(cfg["chunk"])
        print(f"embedding {len(chunks)} chunks for config {cfg_name}...", flush=True)
        vecs = emb.encode([c["text"] for c in chunks])
        stores[cfg_name] = (chunks, vecs)

    results = []
    total = len(CONFIGS) * len(questions)
    done = 0
    t0 = time.time()
    for cfg_name, cfg in CONFIGS.items():
        chunks, vecs = stores[cfg_name]
        for q in questions:
            qv = emb.encode(q["question"])
            sims = vecs @ qv
            top = np.argsort(sims)[::-1][:cfg["top_k"]]
            ctx = "\n\n".join(
                f"[Doc {i+1} | {chunks[i]['source']}] {chunks[i]['text']}"
                for i in top)
            prompt = (f"{SYSTEM}\n\nDocuments:\n{ctx}\n\n"
                      f"Question: {q['question']}\nAnswer:")
            out = llm(prompt, max_tokens=180, temperature=0.1,
                      stop=["Question:", "\n\n\n"])
            text = out["choices"][0]["text"].strip()
            results.append({
                "config": cfg_name, "qid": q["id"], "type": q["type"],
                "question": q["question"],
                "retrieved": [chunks[i]["id"] for i in top],
                "retrieved_scores": [round(float(sims[i]), 4) for i in top],
                "output": text,
            })
            done += 1
            if done % 10 == 0:
                el = time.time() - t0
                print(f"  {done}/{total}  ({el/60:.1f} min)", flush=True)

    fp = os.path.join(BASE, "results.json")
    with open(fp, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    print(f"done: {len(results)} generations -> {fp}")


if __name__ == "__main__":
    main()
