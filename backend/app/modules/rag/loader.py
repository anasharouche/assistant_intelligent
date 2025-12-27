from pathlib import Path
from pypdf import PdfReader
import docx


def load_text(file_path: str) -> str:
    path = Path(file_path)

    if path.suffix.lower() == ".pdf":
        reader = PdfReader(file_path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if path.suffix.lower() == ".docx":
        document = docx.Document(file_path)
        return "\n".join(p.text for p in document.paragraphs)

    raise ValueError("Unsupported document format")
