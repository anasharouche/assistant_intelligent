from datetime import datetime
from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: int
    title: str
    doc_type: str
    file_path: str
    created_at: datetime
