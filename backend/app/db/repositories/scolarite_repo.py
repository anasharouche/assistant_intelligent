from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.models.student import Student
from app.db.models.module import Module
from app.db.models.timetable_session import TimetableSession
from app.db.models.teacher import Teacher


def get_student_by_user_id(db: Session, user_id: int) -> Student | None:
    stmt = select(Student).where(Student.user_id == user_id)
    return db.execute(stmt).scalars().first()


def get_teacher_by_user_id(db: Session, user_id: int) -> Teacher | None:
    stmt = select(Teacher).where(Teacher.user_id == user_id)
    return db.execute(stmt).scalars().first()


def get_modules_for_student(db: Session, student: Student) -> list[Module]:
    stmt = select(Module).where(
        Module.filiere_id == student.filiere_id,
        Module.niveau == student.niveau
    ).order_by(Module.code.asc())
    return list(db.execute(stmt).scalars().all())


def get_timetable_for_group(
    db: Session,
    groupe_id: int,
    date_from: date,
    date_to: date,
) -> list[TimetableSession]:
    stmt = (
        select(TimetableSession)
        .where(
            TimetableSession.groupe_id == groupe_id,
            TimetableSession.date >= date_from,
            TimetableSession.date <= date_to,
        )
        .order_by(TimetableSession.date.asc(), TimetableSession.start_time.asc())
    )
    return list(db.execute(stmt).scalars().all())


def get_teacher_sessions(
    db: Session,
    teacher_id: int,
    date_from: date,
    date_to: date,
) -> list[TimetableSession]:
    stmt = (
        select(TimetableSession)
        .where(
            TimetableSession.teacher_id == teacher_id,
            TimetableSession.date >= date_from,
            TimetableSession.date <= date_to,
        )
        .order_by(TimetableSession.date.asc(), TimetableSession.start_time.asc())
    )
    return list(db.execute(stmt).scalars().all())
