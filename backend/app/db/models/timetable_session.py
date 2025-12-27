from sqlalchemy import String, ForeignKey, Date, Time
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class TimetableSession(Base):
    __tablename__ = "timetable_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)

    date: Mapped[str] = mapped_column(Date, index=True)
    start_time: Mapped[str] = mapped_column(Time)
    end_time: Mapped[str] = mapped_column(Time)

    room: Mapped[str] = mapped_column(String(50))

    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id"))
    groupe_id: Mapped[int] = mapped_column(ForeignKey("groupes.id"))
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id"))
