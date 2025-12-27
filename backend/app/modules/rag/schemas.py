from pydantic import BaseModel, Field

class RagQueryIn(BaseModel):
    question: str = Field(..., min_length=5)

class RagQueryOut(BaseModel):
    answer: str
    sources: list[str]
