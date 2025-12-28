from __future__ import annotations

import os
import re
from datetime import datetime
from typing import Final


class LocalPdfStorage:
    BASE_DIR: Final[str] = os.path.normpath("storage/schedules")

    def __init__(self) -> None:
        os.makedirs(self.BASE_DIR, exist_ok=True)

    def save_pdf(self, *, content: bytes, filename: str) -> str:
        safe_name = self._sanitize_filename(filename)
        stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        final_name = f"{stamp}_{safe_name}"

        path = os.path.normpath(os.path.join(self.BASE_DIR, final_name))

        # Anti path traversal
        if not path.startswith(self.BASE_DIR):
            raise ValueError("Invalid filename")

        with open(path, "wb") as f:
            f.write(content)

        return path

    def read_file(self, file_path: str) -> bytes:
        path = os.path.normpath(file_path)
        with open(path, "rb") as f:
            return f.read()

    def exists(self, file_path: str) -> bool:
        return os.path.exists(os.path.normpath(file_path))

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        name = name.strip()
        # keep letters, digits, dot, dash, underscore
        name = re.sub(r"[^a-zA-Z0-9.\-_]+", "_", name)
        if not name.lower().endswith(".pdf"):
            name += ".pdf"
        return name
