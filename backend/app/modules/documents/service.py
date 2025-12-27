import os
import shutil
from fastapi import UploadFile, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from sqlalchemy.orm import Session
from app.db.repositories.document_repo import (
    create_document,
    list_documents,
    get_document,
    delete_document,
)

BASE_STORAGE = "storage/documents"
ALLOWED_EXTENSIONS = {".pdf", ".docx"}


def save_uploaded_file(file: UploadFile) -> str:
    _, ext = os.path.splitext(file.filename.lower())
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Unsupported file type",
        )

    os.makedirs(BASE_STORAGE, exist_ok=True)
    file_path = os.path.join(BASE_STORAGE, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file_path


def upload_document(
    db: Session,
    title: str,
    doc_type: str,
    file: UploadFile,
):
    file_path = save_uploaded_file(file)
    return create_document(db, title, doc_type, file_path)


def list_all_documents(db: Session):
    return list_documents(db)


def remove_document(db: Session, doc_id: int):
    doc = get_document(db, doc_id)
    if not doc:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Document not found")

    # Delete file
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    delete_document(db, doc)
