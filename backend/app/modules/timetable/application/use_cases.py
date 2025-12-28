from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List

from app.modules.timetable.domain.models import SchedulePdf
from app.modules.timetable.domain.policy import StudentContext, can_access_schedule
from app.modules.timetable.domain.ports import ScheduleRepository, FileStorage
from app.db.repositories.student_repo import get_student_by_user_id
from app.modules.timetable.infrastructure.repositories import SqlAlchemyScheduleRepository
from app.modules.timetable.rag.indexer import index_timetable_pdf


@dataclass(frozen=True)
class UploadScheduleCommand:
    group_id: int
    title: str
    period: Optional[str]
    pdf_bytes: bytes
    original_filename: str
    uploaded_by: int


class UploadScheduleUseCase:
    def __init__(self, repo: ScheduleRepository, storage: FileStorage):
        self.repo = repo
        self.storage = storage

    def execute(self, cmd: UploadScheduleCommand) -> SchedulePdf:
        if not cmd.pdf_bytes:
            raise ValueError("Empty PDF")
        if not cmd.original_filename.lower().endswith(".pdf"):
            raise ValueError("Only PDF allowed")

        file_path = self.storage.save_pdf(
            content=cmd.pdf_bytes,
            filename=cmd.original_filename,
        )

        schedule = self.repo.create(
            group_id=cmd.group_id,
            title=cmd.title,
            period=cmd.period,
            file_path=file_path,
            uploaded_by=cmd.uploaded_by,
        )

        # Indexation RAG timetable (ne casse pas la création)
        try:
            index_timetable_pdf(
                pdf_path=schedule.file_path,
                group_id=schedule.group_id,
            )
        except Exception:
            # important : ne pas casser l'upload si RAG down
            pass

        return schedule


class GetStudentSchedulesUseCase:
    def __init__(self, repo: ScheduleRepository):
        self.repo = repo

    def execute(self, student: StudentContext) -> List[SchedulePdf]:
        return self.repo.list_for_group(student.group_id)


class GetScheduleForStudentUseCase:
    def __init__(self, repo: ScheduleRepository):
        self.repo = repo

    def execute(self, *, student: StudentContext, schedule_id: int) -> SchedulePdf:
        schedule = self.repo.get_by_id(schedule_id)
        if not schedule:
            raise FileNotFoundError("Schedule not found")

        if not can_access_schedule(student, schedule.group_id):
            raise PermissionError("Not allowed")

        return schedule


class DownloadSchedulePdfUseCase:
    def __init__(self, repo: ScheduleRepository, storage: FileStorage):
        self.repo = repo
        self.storage = storage

    def execute(self, *, student: StudentContext, schedule_id: int) -> tuple[str, bytes]:
        schedule = self.repo.get_by_id(schedule_id)
        if not schedule:
            raise FileNotFoundError("Schedule not found")

        if not can_access_schedule(student, schedule.group_id):
            raise PermissionError("Not allowed")

        if not self.storage.exists(schedule.file_path):
            raise FileNotFoundError("PDF not found on disk")

        content = self.storage.read_file(schedule.file_path)
        return schedule.title, content


class GetMyTimetableUseCase:
    """
    Retourne les PDFs d'emploi du temps du groupe de l'étudiant
    """
    def __init__(self, db):
        self.db = db
        self.repo: ScheduleRepository = SqlAlchemyScheduleRepository(db)

    def execute(self, user_id: int):
        student = get_student_by_user_id(self.db, user_id)

        if not student:
            raise ValueError("Student profile not found")

        if not student.groupe_id:
            raise ValueError("Student group not set")

        return self.repo.list_for_group(student.groupe_id)
