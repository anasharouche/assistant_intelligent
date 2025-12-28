from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.security import get_current_user
from app.db.models import User

from app.modules.rag.api.schemas import (
    RagQueryIn,
    RagQueryOut,
    RagIndexIn,
    RagContextItem,
)
from app.modules.rag.application.use_cases import (
    IndexDocumentUseCase,
    QueryRagUseCase,
)
from app.modules.rag.infrastructure.llm_gateway import get_llm_gateway
from app.modules.rag.domain.models import RagAnswer

router = APIRouter(prefix="/rag", tags=["RAG"])


def _build_container(db: Session):
    """
    Mini container de dépendances (adapté PFE).
    """
    llm = get_llm_gateway()
    return (
        IndexDocumentUseCase(db=db),
        QueryRagUseCase(db=db, llm=llm),
    )


@router.post("/index")
def index_rag_document(
    payload: RagIndexIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    index_uc, _ = _build_container(db)

    try:
        result = index_uc.execute(payload.document_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "status": "indexed",
        "document_id": payload.document_id,
        **result,
    }


@router.post("/query", response_model=RagQueryOut)
def query_rag(
    payload: RagQueryIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _, query_uc = _build_container(db)

    # 1️⃣ Use Case retourne un objet métier
    result: RagAnswer = query_uc.execute(payload.question)

    # 2️⃣ Adaptation DOMAIN → API DTO
    return RagQueryOut(
        answer=result.answer,
        sources=result.sources,
        contexts=[
            RagContextItem(
                source=c.source,
                page=c.page,
                score=c.score,
                text=c.text,
            )
            for c in result.contexts
        ],
    )
