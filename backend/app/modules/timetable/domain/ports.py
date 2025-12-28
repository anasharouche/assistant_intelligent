from __future__ import annotations
from typing import Protocol, Optional, List
from app.modules.timetable.domain.models import SchedulePdf


class ScheduleRepository(Protocol):
    def create(
        self,
        *,
        group_id: int,
        title: str,
        period: str | None,
        file_path: str,
        uploaded_by: int,
    ) -> SchedulePdf:
        ...

    def get_latest_for_group(self, group_id: int) -> Optional[SchedulePdf]:
        ...

    def get_by_id(self, schedule_id: int) -> Optional[SchedulePdf]:
        ...

    def list_for_group(self, group_id: int) -> List[SchedulePdf]:
        ...


class FileStorage(Protocol):
    def save_pdf(self, *, content: bytes, filename: str) -> str:
        """
        Sauvegarde le PDF et retourne le file_path.
        """
        ...

    def read_file(self, file_path: str) -> bytes:
        ...

    def exists(self, file_path: str) -> bool:
        ...
