import os
import pickle
from typing import List, Tuple

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from app.modules.rag.text_extractor import extract_text
from app.modules.rag.chunking import chunk_text


VECTOR_DIR = "storage/vector_store"
VECTOR_PATH = os.path.join(VECTOR_DIR, "index.faiss")
META_PATH = os.path.join(VECTOR_DIR, "meta.pkl")

os.makedirs(VECTOR_DIR, exist_ok=True)

model = SentenceTransformer("all-MiniLM-L6-v2")
EMBED_DIM = 384


def load_store() -> Tuple[faiss.Index, list]:
    if os.path.exists(VECTOR_PATH) and os.path.exists(META_PATH):
        index = faiss.read_index(VECTOR_PATH)
        with open(META_PATH, "rb") as f:
            meta = pickle.load(f)
    else:
        index = faiss.IndexFlatL2(EMBED_DIM)
        meta = []
    return index, meta


def save_store(index: faiss.Index, meta: list):
    faiss.write_index(index, VECTOR_PATH)
    with open(META_PATH, "wb") as f:
        pickle.dump(meta, f)


def index_document(
    document_id: int,
    file_path: str,
    chunk_size: int = 900,
    chunk_overlap: int = 150,
) -> dict:

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    text = extract_text(file_path)
    chunks = chunk_text(text, chunk_size, chunk_overlap)

    if not chunks:
        return {"indexed_chunks": 0}

    index, meta = load_store()

    embeddings = model.encode(chunks, convert_to_numpy=True).astype(np.float32)
    index.add(embeddings)

    for chunk in chunks:
        meta.append({
            "document_id": document_id,
            "source": os.path.basename(file_path),
            "file_path": file_path,
            "text": chunk,
        })

    save_store(index, meta)

    return {"indexed_chunks": len(chunks)}


def retrieve_context(question: str, k: int = 5):
    index, meta = load_store()

    if index.ntotal == 0:
        return [], []

    q_emb = model.encode([question], convert_to_numpy=True).astype(np.float32)
    _, idxs = index.search(q_emb, k)

    chunks, sources = [], []

    for i in idxs[0]:
        if i < len(meta):
            chunks.append(meta[i]["text"])
            sources.append(meta[i]["source"])

    return chunks, sorted(set(sources))


def build_prompt(question: str, context_chunks: List[str]) -> str:
    context = "\n\n".join(context_chunks)

    return f"""
Tu es un assistant administratif du service scolarité.
Réponds UNIQUEMENT à partir du contexte ci-dessous.
Si l'information n'existe pas, dis clairement que tu ne sais pas.

CONTEXTE :
{context}

QUESTION :
{question}

RÉPONSE :
""".strip()
