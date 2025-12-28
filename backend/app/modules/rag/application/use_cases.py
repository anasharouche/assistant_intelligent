from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.db.repositories.document_repo import get_document
from app.modules.rag.infrastructure.vector_store_faiss import (
    index_document,
    retrieve_context,
)
from app.modules.rag.infrastructure.llm_gateway import LlmGateway
from app.modules.rag.domain.policy import select_normative_rule
from app.modules.rag.domain.models import RetrievedContext, RagAnswer


class IndexDocumentUseCase:
    """
    Cas d’usage : indexation d’un document pédagogique dans le RAG.
    """

    def __init__(self, db: Session):
        self.db = db

    def execute(self, document_id: int) -> Dict[str, Any]:
        doc = get_document(self.db, document_id)
        if not doc:
            raise FileNotFoundError("Document not found")

        file_path = getattr(doc, "file_path", None)
        if not file_path:
            raise ValueError("Document file_path missing")

        return index_document(
            document_id=document_id,
            file_path=file_path,
        )


class QueryRagUseCase:
    """
    Cas d’usage : interrogation du RAG avec application des règles métier.
    """

    def __init__(self, db: Session, llm: LlmGateway):
        self.db = db
        self.llm = llm

    @staticmethod
    def _force_utf8(text: str) -> str:
        """
        Sécurise l'encodage UTF-8 (Windows / FastAPI / LLM).
        """
        if not text:
            return ""
        return text.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")

    def execute(self, question: str) -> RagAnswer:

        # 1️⃣ Recherche vectorielle (INFRA)
        raw_contexts, sources = retrieve_context(question, k=5)

        # 2️⃣ Adaptation INFRA → DOMAIN (OBLIGATOIRE)
        contexts: List[RetrievedContext] = [
            RetrievedContext(
                source=c["source"],
                page=c["page"],
                score=c["score"],
                text=c["text"],
                document_id=c.get("document_id"),
                chunk_index=c.get("chunk_index"),
            )
            for c in raw_contexts
        ]

        # 3️⃣ Application politique métier
        rule = select_normative_rule(contexts)

        if not rule:
            return RagAnswer(
                answer="Je ne sais pas.",
                sources=sources,
                contexts=contexts,
            )

        # 4️⃣ Prompt contrôlé (pas d’hallucination)
        prompt = f"""
Tu es un assistant administratif du service scolarité.
Réponds uniquement à partir de la règle fournie, sans interprétation.

RÈGLE ADMINISTRATIVE :
{rule}

QUESTION :
{question}

RÉPONSE :
""".strip()

        answer = self.llm.generate(prompt)
        answer = self._force_utf8(answer)

        return RagAnswer(
            answer=answer,
            sources=sources,
            contexts=contexts,
        )
