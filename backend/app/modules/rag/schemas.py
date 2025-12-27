from pydantic import BaseModel, Field
from typing import List, Optional


class RagQueryIn(BaseModel):
    question: str = Field(..., min_length=2)


class RagContextItem(BaseModel):
    source: str
    page: int
    score: float
    text: str


class RagQueryOut(BaseModel):
    answer: str
    sources: List[str] = []
    contexts: List[RagContextItem] = [] 


class RagIndexIn(BaseModel):
    document_id: int
