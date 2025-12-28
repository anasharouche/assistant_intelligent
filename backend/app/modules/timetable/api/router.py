from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.security import get_current_user
from app.db.models import User 

from app.modules.timetable.domain.policy import StudentContext
from app.modules.timetable.infrastructure.repositories import SqlAlchemyScheduleRepository
from app.modules.timetable.infrastructure.storage import LocalPdfStorage
from app.modules.timetable.application.use_cases import (
    UploadScheduleUseCase,
    UploadScheduleCommand,
    GetStudentSchedulesUseCase,
    GetScheduleForStudentUseCase,
    DownloadSchedulePdfUseCase,
    GetMyTimetableUseCase,
)
from app.db.repositories.student_repo import get_student_by_user_id
from app.modules.timetable.api.schemas import ScheduleOut
from app.modules.timetable.rag.service import ask_timetable

router = APIRouter(prefix="/timetable", tags=["Timetable"])


def _container(db: Session):
    repo = SqlAlchemyScheduleRepository(db)
    storage = LocalPdfStorage()
    return repo, storage


def _require_scolarite(user: User) -> None:
    # adapte au nom de rôle chez toi (ex: "SCOLARITE" / "ADMIN")
    if getattr(user, "role", None) not in ("SCOLARITE", "ADMIN"):
        raise HTTPException(status_code=403, detail="Forbidden")




@router.post("/upload", response_model=ScheduleOut)
async def upload_schedule_pdf(
    group_id: int = Form(...),
    title: str = Form(...),
    period: str | None = Form(None),
    pdf: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_scolarite(current_user)

    if pdf.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="Only PDF allowed")

    content = await pdf.read()
    repo, storage = _container(db)

    uc = UploadScheduleUseCase(repo=repo, storage=storage)

    try:
        schedule = uc.execute(
            UploadScheduleCommand(
                group_id=group_id,
                title=title,
                period=period,
                pdf_bytes=content,
                original_filename=pdf.filename or "schedule.pdf",
                uploaded_by=current_user.id,
            )
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return ScheduleOut(
        id=schedule.id,
        group_id=schedule.group_id,
        title=schedule.title,
        period=schedule.period,
        created_at=schedule.created_at,
    )


@router.get("/me")
def get_my_timetable(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        uc = GetMyTimetableUseCase(db)
        schedules = uc.execute(user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return schedules

@router.get("/{schedule_id}", response_model=ScheduleOut)
def get_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo, _ = _container(db)

    # Récupération du student réel
    student_row = get_student_by_user_id(db, current_user.id)
    if not student_row:
        raise HTTPException(status_code=400, detail="Student profile not found")

    if not student_row.groupe_id:
        raise HTTPException(status_code=400, detail="Student group not set")

    student = StudentContext(
        user_id=current_user.id,
        group_id=student_row.groupe_id,
    )

    uc = GetScheduleForStudentUseCase(repo=repo)

    try:
        s = uc.execute(student=student, schedule_id=schedule_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Schedule not found")
    except PermissionError:
        raise HTTPException(status_code=403, detail="Forbidden")

    return ScheduleOut(
        id=s.id,
        group_id=s.group_id,
        title=s.title,
        period=s.period,
        created_at=s.created_at,
    )


@router.get("/{schedule_id}/download")
def download_schedule_pdf(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo, storage = _container(db)

    # ✅ Récupération du student (source métier correcte)
    student_row = get_student_by_user_id(db, current_user.id)
    if not student_row or not student_row.groupe_id:
        raise HTTPException(status_code=400, detail="Student group not set")

    student = StudentContext(
        user_id=current_user.id,
        group_id=student_row.groupe_id,
    )

    uc = DownloadSchedulePdfUseCase(repo=repo, storage=storage)

    try:
        title, content = uc.execute(student=student, schedule_id=schedule_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except PermissionError:
        raise HTTPException(status_code=403, detail="Forbidden")

    filename = f"{title}.pdf".replace("/", "_").replace("\\", "_")

    return Response(
        content=content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        },
    )


@router.post("/ask")
def ask_my_timetable(
    question: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    student = get_student_by_user_id(db, current_user.id)

    if not student or not student.groupe_id:
        raise HTTPException(status_code=400, detail="Student group not set")

    answer = ask_timetable(
        question=question,
        group_id=student.groupe_id,
    )

    return {
        "question": question,
        "answer": answer,
    }