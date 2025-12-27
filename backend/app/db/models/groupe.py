from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Groupe(Base):
    __tablename__ = "groupes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    filiere_id: Mapped[int] = mapped_column(ForeignKey("filieres.id"))
    niveau: Mapped[str] = mapped_column(String(50))
