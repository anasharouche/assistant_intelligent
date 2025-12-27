import faiss
import numpy as np
from pathlib import Path
import pickle

VECTOR_DIM = 384
STORE_PATH = Path("storage/vector_store")


class VectorStore:
    def __init__(self):
        self.index = faiss.IndexFlatL2(VECTOR_DIM)
        self.metadata = []

    def add(self, embeddings, metadatas):
        self.index.add(np.array(embeddings))
        self.metadata.extend(metadatas)

    def search(self, query_embedding, top_k: int = 5):
        distances, indices = self.index.search(
            np.array([query_embedding]), top_k
        )
        return [self.metadata[i] for i in indices[0] if i < len(self.metadata)]

    def save(self):
        STORE_PATH.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(STORE_PATH / "index.faiss"))
        with open(STORE_PATH / "meta.pkl", "wb") as f:
            pickle.dump(self.metadata, f)

    def load(self):
        if not (STORE_PATH / "index.faiss").exists():
            return
        self.index = faiss.read_index(str(STORE_PATH / "index.faiss"))
        with open(STORE_PATH / "meta.pkl", "rb") as f:
            self.metadata = pickle.load(f)
