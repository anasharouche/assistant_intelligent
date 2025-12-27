from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.modules.rag.schemas import RagQueryIn, RagQueryOut
from app.modules.rag.service import retrieve_context, build_prompt, index_document
from app.modules.rag.llm import call_llm
from app.core.security import get_current_user
from app.db.models import User
from app.core.deps import get_db
from app.db.repositories.document_repo import get_document_by_id

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/index")
def index_rag_document(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Indexe un document RÉEL depuis la DB :
    payload = { "document_id": 123 }
    """
    document_id = payload.get("document_id")
    if not document_id:
        raise HTTPException(status_code=400, detail="document_id is required")

    doc = get_document_by_id(db, int(document_id))
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    file_path = getattr(doc, "file_path", None)
    if not file_path:
        raise HTTPException(
            status_code=500,
            detail="Document file_path is missing in DB"
        )

    try:
        result = index_document(
            document_id=int(document_id),
            file_path=file_path
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "status": "indexed",
        "document_id": int(document_id),
        "stats": result
    }


@router.post("/query", response_model=RagQueryOut)
def query_rag(
    payload: RagQueryIn,
    current_user: User = Depends(get_current_user),
):
    chunks, sources = retrieve_context(payload.question)
    prompt = build_prompt(payload.question, chunks)
    answer = call_llm(prompt)

    return RagQueryOut(answer=answer, sources=sources)
