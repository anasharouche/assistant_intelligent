from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    code_apogee: Mapped[str] = mapped_column(String(50), unique=True)
    cin: Mapped[str] = mapped_column(String(20), unique=True)
    filiere_id: Mapped[int] = mapped_column(ForeignKey("filieres.id"))
    groupe_id: Mapped[int] = mapped_column(ForeignKey("groupes.id"))
    niveau: Mapped[str] = mapped_column(String(50))
