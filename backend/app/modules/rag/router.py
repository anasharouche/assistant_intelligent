from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.security import get_current_user
from app.db.models import User
from app.db.repositories.document_repo import get_document

from app.modules.rag.schemas import RagQueryIn, RagQueryOut, RagIndexIn, RagContextItem
from app.modules.rag.service import (
    index_document,
    retrieve_context,
    build_prompt,
    extract_fact_answer,
)
from app.modules.rag.llm import call_llm

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/index")
def index_rag_document(
    payload: RagIndexIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = get_document(db, payload.document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    result = index_document(payload.document_id, doc.file_path)

    return {
        "status": "indexed",
        "document_id": payload.document_id,
        **result,
    }


@router.post("/query", response_model=RagQueryOut)
def query_rag(
    payload: RagQueryIn,
    current_user: User = Depends(get_current_user),
):
    contexts, sources = retrieve_context(payload.question)

    if not contexts:
        return RagQueryOut(
            answer="Information non disponible dans les documents.",
            sources=[],
            contexts=[]
        )

    try:
        prompt = build_prompt(payload.question, contexts)
        answer = call_llm(prompt)

        if not answer or "je ne sais pas" in answer.lower():
            raise ValueError()

    except Exception:
        answer = extract_fact_answer(contexts)

    ctx_items = [RagContextItem(**c) for c in contexts]

    return RagQueryOut(
        answer=answer,
        sources=sources,
        contexts=ctx_items
    )
