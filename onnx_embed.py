"""ONNX-based embedding wrapper for all-MiniLM-L6-v2 (Xenova).

Torch-free: uses onnxruntime + tokenizers. Mean-pooling over attention mask,
L2-normalized. API-compatible with sentence-transformers .encode().
"""
import os

import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
ONNX_DIR = os.path.join(BASE, "models", "onnx-minilm")


class OnnxEmbedder:
    def __init__(self):
        import onnxruntime as ort
        from tokenizers import Tokenizer
        self.sess = ort.InferenceSession(
            os.path.join(ONNX_DIR, "model.onnx"),
            providers=["CPUExecutionProvider"])
        # reuse tokenizer.json from the pytorch download (same vocab)
        self.tok = Tokenizer.from_file(os.path.join(BASE, "models", "minilm",
                                                    "tokenizer.json"))

    def encode(self, texts, normalize=True):
        if isinstance(texts, str):
            texts = [texts]
            single = True
        else:
            single = False
        enc = self.tok.encode_batch(texts)
        ids = np.array([e.ids for e in enc], dtype=np.int64)
        mask = np.array([e.attention_mask for e in enc], dtype=np.int64)
        tt = np.array([e.type_ids for e in enc], dtype=np.int64)
        out = self.sess.run(None, {"input_ids": ids,
                                   "attention_mask": mask,
                                   "token_type_ids": tt})[0]
        # mean pooling
        m = np.expand_dims(mask, -1).astype(np.float32)
        emb = (out * m).sum(axis=1) / m.sum(axis=1).clip(min=1e-9)
        if normalize:
            emb = emb / np.linalg.norm(emb, axis=1, keepdims=True).clip(min=1e-9)
        return emb[0] if single else emb
