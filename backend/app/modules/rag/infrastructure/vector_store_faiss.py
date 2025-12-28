from __future__ import annotations

import os
import pickle
from typing import List, Tuple, Dict, Any, Optional

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader

from app.modules.rag.infrastructure.text_utils import normalize_text


# =========================
# CONFIG
# =========================
STORE_DIR = "storage/vector_store"
os.makedirs(STORE_DIR, exist_ok=True)

MODEL = SentenceTransformer("all-MiniLM-L6-v2")
EMB_DIM = 384


def _paths(namespace: str) -> tuple[str, str]:
    """
    Chaque namespace a son propre index et meta.
    Ex: index__timetable_group_10.faiss / meta__timetable_group_10.pkl
    """
    safe = (namespace or "default").replace("/", "_").replace("\\", "_").replace(" ", "_")
    vector_path = os.path.join(STORE_DIR, f"index__{safe}.faiss")
    meta_path = os.path.join(STORE_DIR, f"meta__{safe}.pkl")
    return vector_path, meta_path


def _load_store(namespace: str = "default") -> Tuple[faiss.Index, List[Dict[str, Any]]]:
    vector_path, meta_path = _paths(namespace)

    if os.path.exists(vector_path) and os.path.exists(meta_path):
        index = faiss.read_index(vector_path)
        with open(meta_path, "rb") as f:
            meta = pickle.load(f)
    else:
        index = faiss.IndexFlatIP(EMB_DIM)
        meta = []
    return index, meta


def _save_store(index: faiss.Index, meta: List[Dict[str, Any]], namespace: str = "default") -> None:
    vector_path, meta_path = _paths(namespace)
    faiss.write_index(index, vector_path)
    with open(meta_path, "wb") as f:
        pickle.dump(meta, f)


def _normalize(v: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(v, axis=1, keepdims=True) + 1e-12
    return v / norms


# =========================
# PUBLIC API (DOCS RAG)
# =========================
def index_document(
    document_id: int,
    file_path: str,
    *,
    namespace: str = "default",
) -> Dict[str, Any]:
    """
    Indexe un document PDF (règlement, docs pédagogiques, etc.) dans FAISS.
    Namespace par défaut = "default" => ne casse pas l'existant.
    """
    index, meta = _load_store(namespace)

    normalized_path = os.path.normpath(file_path)
    if not os.path.exists(normalized_path):
        raise FileNotFoundError(f"PDF introuvable : {normalized_path}")

    reader = PdfReader(normalized_path)
    chunks: List[str] = []
    metadatas: List[Dict[str, Any]] = []

    for page_num, page in enumerate(reader.pages, start=1):
        raw_text = page.extract_text() or ""
        text = normalize_text(raw_text)
        if not text:
            continue

        for i in range(0, len(text), 900):
            chunk = text[i:i + 900].strip()
            if not chunk:
                continue

            chunks.append(chunk)
            metadatas.append({
                "document_id": document_id,
                "source": normalized_path,
                "page": page_num,
                "text": chunk,
                "namespace": namespace,
            })

    if not chunks:
        raise ValueError("Document vide ou illisible")

    embeddings = MODEL.encode(chunks, convert_to_numpy=True).astype("float32")
    embeddings = _normalize(embeddings)

    index.add(embeddings)
    meta.extend(metadatas)
    _save_store(index, meta, namespace)

    return {
        "namespace": namespace,
        "pages": len(reader.pages),
        "chunks": len(chunks),
        "vectors": index.ntotal,
    }


def retrieve_context(
    question: str,
    k: int = 5,
    *,
    namespace: str = "default",
) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Récupère des chunks depuis un namespace donné.
    Namespace par défaut = "default" => ne casse pas l'existant.
    """
    index, meta = _load_store(namespace)
    if index.ntotal == 0:
        return [], []

    q_emb = MODEL.encode([question], convert_to_numpy=True).astype("float32")
    q_emb = _normalize(q_emb)

    scores, idxs = index.search(q_emb, k)

    contexts: List[Dict[str, Any]] = []
    sources = set()

    for score, idx in zip(scores[0], idxs[0]):
        if idx < 0 or idx >= len(meta):
            continue

        m = meta[idx]
        contexts.append({
            "source": m.get("source", ""),
            "page": int(m.get("page", 0)),
            "score": float(score),
            "text": normalize_text(m.get("text", "")),
            "document_id": m.get("document_id"),
            "chunk_index": m.get("chunk_index"),
        })
        if m.get("source"):
            sources.add(m["source"])

    return contexts, list(sources)


# =========================
# PUBLIC API (TIMETABLE)
# =========================
def index_pdf_for_namespace(
    *,
    file_path: str,
    namespace: str,
    extra_metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Indexe un PDF dans un namespace spécifique (ex: timetable_group_10).
    """
    index, meta = _load_store(namespace)

    normalized_path = os.path.normpath(file_path)
    if not os.path.exists(normalized_path):
        raise FileNotFoundError(f"PDF introuvable : {normalized_path}")

    reader = PdfReader(normalized_path)
    chunks: List[str] = []
    metadatas: List[Dict[str, Any]] = []
    extra_metadata = extra_metadata or {}

    for page_num, page in enumerate(reader.pages, start=1):
        raw_text = page.extract_text() or ""
        text = normalize_text(raw_text)
        if not text:
            continue

        # chunking (conservatif)
        for i in range(0, len(text), 900):
            chunk = text[i:i + 900].strip()
            if not chunk:
                continue

            chunks.append(chunk)
            metadatas.append({
                "document_id": None,
                "source": normalized_path,
                "page": page_num,
                "text": chunk,
                "namespace": namespace,
                **extra_metadata,
            })

    if not chunks:
        raise ValueError("PDF vide ou illisible")

    embeddings = MODEL.encode(chunks, convert_to_numpy=True).astype("float32")
    embeddings = _normalize(embeddings)

    index.add(embeddings)
    meta.extend(metadatas)
    _save_store(index, meta, namespace)

    return {
        "namespace": namespace,
        "pages": len(reader.pages),
        "chunks": len(chunks),
        "vectors": index.ntotal,
    }
