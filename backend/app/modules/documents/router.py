from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.modules.auth.deps import require_roles
from app.modules.documents.schemas import DocumentOut
from app.modules.documents.service import (
    upload_document,
    list_all_documents,
    remove_document,
)
from app.shared.responses import ApiResponse

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=ApiResponse[DocumentOut])
def upload(
    title: str = Form(...),
    doc_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(require_roles(["SCOLARITE", "ADMIN"])),
):
    doc = upload_document(db, title, doc_type, file)
    return ApiResponse(data=DocumentOut.model_validate(doc.__dict__))


@router.get("", response_model=ApiResponse[list[DocumentOut]])
def list_docs(
    db: Session = Depends(get_db),
    user=Depends(require_roles(["SCOLARITE", "ADMIN"])),
):
    docs = list_all_documents(db)
    return ApiResponse(data=[DocumentOut.model_validate(d.__dict__) for d in docs])


@router.delete("/{doc_id}", response_model=ApiResponse[None])
def delete_doc(
    doc_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles(["SCOLARITE", "ADMIN"])),
):
    remove_document(db, doc_id)
    return ApiResponse(data=None)
