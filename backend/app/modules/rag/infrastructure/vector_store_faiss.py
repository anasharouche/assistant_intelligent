import os
import pickle
from typing import List, Tuple, Dict, Any

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
from app.modules.rag.infrastructure.text_utils import normalize_text


# =========================
# CONFIG
# =========================
VECTOR_PATH = "storage/vector_store/index.faiss"
META_PATH = "storage/vector_store/meta.pkl"
os.makedirs("storage/vector_store", exist_ok=True)

MODEL = SentenceTransformer("all-MiniLM-L6-v2")
EMB_DIM = 384


# =========================
# INTERNAL STORE
# =========================
def _load_store() -> Tuple[faiss.Index, List[Dict[str, Any]]]:
    if os.path.exists(VECTOR_PATH) and os.path.exists(META_PATH):
        index = faiss.read_index(VECTOR_PATH)
        with open(META_PATH, "rb") as f:
            meta = pickle.load(f)
    else:
        index = faiss.IndexFlatIP(EMB_DIM)
        meta = []
    return index, meta


def _save_store(index: faiss.Index, meta: List[Dict[str, Any]]) -> None:
    faiss.write_index(index, VECTOR_PATH)
    with open(META_PATH, "wb") as f:
        pickle.dump(meta, f)


def _normalize(v: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(v, axis=1, keepdims=True) + 1e-12
    return v / norms


# =========================
# PUBLIC API (PORTS)
# =========================
def index_document(document_id: int, file_path: str) -> Dict[str, Any]:
    """
    Indexe un document PDF dans FAISS avec texte UTF-8 propre.
    """
    index, meta = _load_store()

    reader = PdfReader(file_path)
    chunks = []
    metadatas = []

    for page_num, page in enumerate(reader.pages, start=1):
        raw_text = page.extract_text() or ""
        text = normalize_text(raw_text)

        if not text:
            continue

        # Chunking propre
        for i in range(0, len(text), 900):
            chunk = text[i:i + 900].strip()
            if not chunk:
                continue

            chunks.append(chunk)
            metadatas.append({
                "document_id": document_id,
                "source": file_path,
                "page": page_num,
                "text": chunk,
            })

    if not chunks:
        raise ValueError("Document vide ou illisible")

    embeddings = MODEL.encode(chunks, convert_to_numpy=True).astype("float32")
    embeddings = _normalize(embeddings)

    index.add(embeddings)
    meta.extend(metadatas)

    _save_store(index, meta)

    return {
        "pages": len(reader.pages),
        "chunks": len(chunks),
        "vectors": index.ntotal,
    }


def retrieve_context(
    question: str,
    k: int = 5,
) -> Tuple[List[Dict[str, Any]], List[str]]:

    index, meta = _load_store()
    if index.ntotal == 0:
        return [], []

    q_emb = MODEL.encode([question], convert_to_numpy=True).astype("float32")
    q_emb = _normalize(q_emb)

    scores, idxs = index.search(q_emb, k)

    contexts = []
    sources = set()

    for score, idx in zip(scores[0], idxs[0]):
        if idx < 0 or idx >= len(meta):
            continue

        m = meta[idx]
        contexts.append({
            "source": m["source"],
            "page": m["page"],
            "score": float(score),
            "text": normalize_text(m["text"]),  # sécurité
        })
        sources.add(m["source"])

    return contexts, list(sources)
