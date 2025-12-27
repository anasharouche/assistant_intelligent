from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models.document import Document


def create_document(
    db: Session,
    title: str,
    doc_type: str,
    file_path: str
) -> Document:
    doc = Document(
        title=title,
        doc_type=doc_type,
        file_path=file_path
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def list_documents(db: Session) -> list[Document]:
    stmt = select(Document).order_by(Document.created_at.desc())
    return list(db.execute(stmt).scalars().all())


def get_document(db: Session, doc_id: int) -> Document | None:
    stmt = select(Document).where(Document.id == doc_id)
    return db.execute(stmt).scalars().first()

def get_document_by_id(db: Session, document_id: int) -> Document | None:
    return get_document(db, document_id)


def delete_document(db: Session, doc: Document) -> None:
    db.delete(doc)
    db.commit()
