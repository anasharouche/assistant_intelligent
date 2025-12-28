from pydantic import BaseModel
from typing import List


class RagIndexIn(BaseModel):
    document_id: int


class RagQueryIn(BaseModel):
    question: str


class RagContextItem(BaseModel):
    source: str
    page: int
    score: float
    text: str


class RagQueryOut(BaseModel):
    answer: str
    sources: List[str]
    contexts: List[RagContextItem]
