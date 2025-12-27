import os
import pickle
import re
from typing import List, Tuple, Dict, Any

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader

# =========================
# CONFIG
# =========================
VECTOR_PATH = "storage/vector_store/index.faiss"
META_PATH = "storage/vector_store/meta.pkl"
os.makedirs("storage/vector_store", exist_ok=True)

model = SentenceTransformer("all-MiniLM-L6-v2")
EMB_DIM = 384

# =========================
# RÈGLES MÉTIER (CENTRALISÉES)
# =========================
RULE_KEYWORDS = [
    "est validé si",
    "est validée si",
    "est validé",
    "doit être",
    "est requis",
    "est exigé",
]

# =========================
# STORE
# =========================
def load_store() -> Tuple[faiss.Index, List[Dict[str, Any]]]:
    if os.path.exists(VECTOR_PATH) and os.path.exists(META_PATH):
        index = faiss.read_index(VECTOR_PATH)
        with open(META_PATH, "rb") as f:
            meta = pickle.load(f)
    else:
        index = faiss.IndexFlatIP(EMB_DIM)
        meta = []
    return index, meta


def save_store(index: faiss.Index, meta: List[Dict[str, Any]]) -> None:
    faiss.write_index(index, VECTOR_PATH)
    with open(META_PATH, "wb") as f:
        pickle.dump(meta, f)

# =========================
# PDF EXTRACTION
# =========================
def extract_pages_from_pdf(file_path: str) -> List[Dict[str, Any]]:
    normalized_path = os.path.normpath(file_path)
    if not os.path.exists(normalized_path):
        raise FileNotFoundError(f"PDF introuvable : {normalized_path}")

    reader = PdfReader(normalized_path)
    pages = []

    for i, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append({"page": i, "text": text})

    return pages

# =========================
# CHUNKING
# =========================
def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150) -> List[str]:
    chunks = []
    start = 0
    n = len(text)

    while start < n:
        end = min(start + chunk_size, n)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == n:
            break
        start = max(0, end - overlap)

    return chunks


def _normalize(v: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(v, axis=1, keepdims=True) + 1e-12
    return v / norms

# =========================
# INDEX DOCUMENT
# =========================
def index_document(document_id: int, file_path: str) -> Dict[str, Any]:
    index, meta = load_store()
    pages = extract_pages_from_pdf(file_path)

    if not pages:
        raise ValueError("PDF vide ou illisible.")

    all_chunks, all_meta = [], []

    for p in pages:
        for ci, chunk in enumerate(chunk_text(p["text"])):
            all_chunks.append(chunk)
            all_meta.append({
                "document_id": document_id,
                "source": file_path,
                "page": p["page"],
                "chunk_index": ci,
                "text": chunk,
            })

    emb = model.encode(all_chunks, convert_to_numpy=True).astype("float32")
    emb = _normalize(emb)

    index.add(emb)
    meta.extend(all_meta)
    save_store(index, meta)

    return {
        "stats": {
            "pages_count": len(pages),
            "chunks_count": len(all_chunks),
            "vector_count": int(index.ntotal),
        }
    }

# =========================
# RETRIEVE
# =========================
def retrieve_context(question: str, k: int = 5) -> Tuple[List[Dict[str, Any]], List[str]]:
    index, meta = load_store()

    if index.ntotal == 0:
        return [], []

    q_emb = model.encode([question], convert_to_numpy=True).astype("float32")
    q_emb = _normalize(q_emb)

    scores, idxs = index.search(q_emb, k)

    contexts, sources = [], []

    for score, idx in zip(scores[0], idxs[0]):
        if idx < 0 or idx >= len(meta):
            continue

        m = meta[idx]
        contexts.append({
            "source": m.get("source"),
            "page": int(m.get("page", 0)),
            "score": float(score),
            "text": m.get("text", ""),
        })

        if m.get("source"):
            sources.append(m["source"])

    return contexts, list(set(sources))

# =========================
# EXTRACTION MÉTIER (CLÉ)
# =========================
def extract_fact_answer(contexts: List[Dict[str, Any]]) -> str:
    """
    Extrait UNE règle métier claire côté backend.
    """
    for c in contexts:
        sentences = re.split(r"[.\n]", c["text"])
        for s in sentences:
            s = s.strip()
            if len(s) > 20 and any(k in s.lower() for k in RULE_KEYWORDS):
                return f"{s} (page {c['page']})"

    return "Je ne sais pas."

# =========================
# FILTRAGE CONTEXTES
# =========================
def extract_normative_contexts(contexts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    filtered = []
    for c in contexts:
        if any(k in c["text"].lower() for k in RULE_KEYWORDS):
            filtered.append(c)
    return filtered

# =========================
# PROMPT (LLM = REFORMULATION)
# =========================
def build_prompt(question: str, contexts: List[Dict[str, Any]]) -> str:
    parts = [
        f"[PAGE {c['page']}]\n{c['text']}"
        for c in contexts
    ]

    context_block = "\n\n".join(parts)

    return (
        "Tu es un assistant administratif du service scolarité.\n\n"
        "RÈGLES STRICTES :\n"
        "1) Reformule UNIQUEMENT la règle donnée.\n"
        "2) Ne rajoute aucune information.\n"
        "3) Termine par (page X).\n\n"
        f"CONTEXTE :\n{context_block}\n\n"
        f"QUESTION :\n{question}\n\n"
        "RÉPONSE :"
    )
