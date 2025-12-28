from __future__ import annotations
import numpy as np
from sentence_transformers import SentenceTransformer


class SentenceTransformerEmbedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", emb_dim: int = 384) -> None:
        self.model = SentenceTransformer(model_name)
        self.emb_dim = emb_dim

    @staticmethod
    def _normalize(v: np.ndarray) -> np.ndarray:
        if v.ndim == 1:
            v = v.reshape(1, -1)
        norms = np.linalg.norm(v, axis=1, keepdims=True) + 1e-12
        return v / norms

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        emb = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        emb = emb.astype("float32")
        return self._normalize(emb)

    def embed_query(self, q: str) -> np.ndarray:
        emb = self.model.encode([q], convert_to_numpy=True, show_progress_bar=False)
        emb = emb.astype("float32")
        return self._normalize(emb)
