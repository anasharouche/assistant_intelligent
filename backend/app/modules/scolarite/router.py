from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.modules.auth.deps import require_roles, get_current_user
from app.modules.scolarite.schemas import ModuleOut, TimetableSessionOut
from app.modules.scolarite.service import student_modules, student_timetable, teacher_timetable
from app.shared.responses import ApiResponse


router = APIRouter(prefix="/scolarite", tags=["Scolarite"])


@router.get("/modules/me", response_model=ApiResponse[list[ModuleOut]])
def get_my_modules(
    db: Session = Depends(get_db),
    user=Depends(require_roles(["STUDENT"])),
):
    modules = student_modules(db, user.id)
    return ApiResponse(data=[ModuleOut.model_validate(m.__dict__) for m in modules])


@router.get("/timetable/me", response_model=ApiResponse[list[TimetableSessionOut]])
def get_my_timetable(
    db: Session = Depends(get_db),
    user=Depends(require_roles(["STUDENT"])),
    date_from: date = Query(..., alias="from"),
    date_to: date = Query(..., alias="to"),
):
    sessions = student_timetable(db, user.id, date_from, date_to)
    return ApiResponse(data=[TimetableSessionOut.model_validate(s.__dict__) for s in sessions])


@router.get("/teacher/sessions", response_model=ApiResponse[list[TimetableSessionOut]])
def get_teacher_sessions(
    db: Session = Depends(get_db),
    user=Depends(require_roles(["TEACHER"])),
    date_from: date = Query(..., alias="from"),
    date_to: date = Query(..., alias="to"),
):
    sessions = teacher_timetable(db, user.id, date_from, date_to)
    return ApiResponse(data=[TimetableSessionOut.model_validate(s.__dict__) for s in sessions])
