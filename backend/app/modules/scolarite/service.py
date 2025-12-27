from datetime import date
from fastapi import HTTPException
from starlette.status import HTTP_404_NOT_FOUND

from sqlalchemy.orm import Session
from app.db.repositories.scolarite_repo import (
    get_student_by_user_id,
    get_teacher_by_user_id,
    get_modules_for_student,
    get_timetable_for_group,
    get_teacher_sessions,
)


def student_modules(db: Session, user_id: int):
    student = get_student_by_user_id(db, user_id)
    if not student:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Student profile not found")
    return get_modules_for_student(db, student)


def student_timetable(db: Session, user_id: int, date_from: date, date_to: date):
    student = get_student_by_user_id(db, user_id)
    if not student:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Student profile not found")
    return get_timetable_for_group(db, student.groupe_id, date_from, date_to)


def teacher_timetable(db: Session, user_id: int, date_from: date, date_to: date):
    teacher = get_teacher_by_user_id(db, user_id)
    if not teacher:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Teacher profile not found")
    return get_teacher_sessions(db, teacher.id, date_from, date_to)
