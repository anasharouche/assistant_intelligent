from dataclasses import dataclass
from typing import Optional, List


@dataclass(frozen=True)
class RetrievedContext:
    """
    Objet métier représentant un contexte récupéré depuis le RAG.
    """
    source: str
    page: int
    score: float
    text: str
    document_id: Optional[int] = None
    chunk_index: Optional[int] = None


@dataclass(frozen=True)
class RagAnswer:
    """
    Réponse finale retournée par le RAG.
    """
    answer: str
    sources: List[str]
    contexts: List[RetrievedContext]
