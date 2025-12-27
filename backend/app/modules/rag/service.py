import os
import pickle
import faiss
from typing import List, Dict

from sentence_transformers import SentenceTransformer
from pypdf import PdfReader

VECTOR_PATH = "storage/vector_store/index.faiss"
META_PATH = "storage/vector_store/meta.pkl"

os.makedirs("storage/vector_store", exist_ok=True)

# Modèle d'embedding
model = SentenceTransformer("all-MiniLM-L6-v2")


# =========================
# STORE
# =========================
def load_store():
    if os.path.exists(VECTOR_PATH) and os.path.exists(META_PATH):
        index = faiss.read_index(VECTOR_PATH)
        with open(META_PATH, "rb") as f:
            meta = pickle.load(f)
    else:
        index = faiss.IndexFlatL2(384)
        meta = []

    return index, meta


def save_store(index, meta):
    faiss.write_index(index, VECTOR_PATH)
    with open(META_PATH, "wb") as f:
        pickle.dump(meta, f)


# =========================
# PDF TEXT EXTRACTION
# =========================
def extract_text_from_pdf(file_path: str) -> str:
    normalized_path = os.path.normpath(file_path)

    if not os.path.exists(normalized_path):
        raise FileNotFoundError(f"PDF introuvable : {normalized_path}")

    reader = PdfReader(normalized_path)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text.strip()


# =========================
# CHUNKING
# =========================
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap

    return chunks


# =========================
# INDEX DOCUMENT (CORRIGÉ)
# =========================
def index_document(
    document_id: int,
    file_path: str,
) -> Dict:
    index, meta = load_store()

    # 1️⃣ Extraire le texte réel
    text = extract_text_from_pdf(file_path)

    if not text:
        raise ValueError("PDF vide ou illisible")

    # 2️⃣ Découper en chunks
    chunks = chunk_text(text)

    if not chunks:
        raise ValueError("Aucun chunk généré depuis le document")

    # 3️⃣ Embeddings
    embeddings = model.encode(chunks)

    # 4️⃣ Index FAISS
    index.add(embeddings)

    # 5️⃣ Meta
    for chunk in chunks:
        meta.append({
            "document_id": document_id,
            "source": file_path,
            "text": chunk,
        })

    save_store(index, meta)

    # ✅ RETOUR EXPLICITE (clé de la correction)
    return {
        "chunks_count": len(chunks),
        "vector_count": index.ntotal,
    }


# =========================
# RETRIEVE
# =========================
def retrieve_context(question: str, k: int = 5):
    index, meta = load_store()

    if index.ntotal == 0:
        return [], []

    q_emb = model.encode([question])
    _, idxs = index.search(q_emb, k)

    chunks = []
    sources = []

    for i in idxs[0]:
        if i < len(meta):
            chunks.append(meta[i]["text"])
            sources.append(meta[i]["source"])

    return chunks, list(set(sources))


# =========================
# PROMPT
# =========================
def build_prompt(question: str, context_chunks: List[str]) -> str:
    context = "\n\n".join(context_chunks)

    return f"""
Tu es un assistant administratif du service scolarité.
Réponds UNIQUEMENT avec le contexte fourni.
Si la réponse n'est pas dans le contexte, dis clairement que tu ne sais pas.

CONTEXTE :
{context}

QUESTION :
{question}

RÉPONSE :
""".strip()
