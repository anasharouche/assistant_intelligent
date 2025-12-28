from __future__ import annotations

from app.modules.rag.infrastructure.vector_store_faiss import index_pdf_for_namespace


def index_timetable_pdf(*, pdf_path: str, group_id: int) -> dict:
    """
    Indexe un PDF d'emploi du temps dans un namespace séparé par groupe.
    Cela évite de mélanger avec le règlement (namespace default).
    """
    namespace = f"timetable_group_{group_id}"

    return index_pdf_for_namespace(
        file_path=pdf_path,
        namespace=namespace,
        extra_metadata={"group_id": group_id},
    )
