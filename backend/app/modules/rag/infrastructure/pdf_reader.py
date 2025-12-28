import os
from typing import List, Dict, Any
from pypdf import PdfReader
from app.modules.rag.infrastructure.text_utils import normalize_text


def extract_pages(file_path: str) -> List[Dict[str, Any]]:
    normalized = os.path.normpath(file_path)
    if not os.path.exists(normalized):
        raise FileNotFoundError(f"PDF introuvable : {normalized}")

    reader = PdfReader(normalized)
    pages = []

    for i, page in enumerate(reader.pages, start=1):
        raw_text = page.extract_text() or ""
        text = normalize_text(raw_text)

        if text:
            pages.append({
                "page": i,
                "text": text,
            })

    return pages
