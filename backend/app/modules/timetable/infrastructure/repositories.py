from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy import desc, Column, Integer, String, Text, DateTime

from app.db.base import Base
from app.modules.timetable.domain.models import SchedulePdf
from app.modules.timetable.domain.ports import ScheduleRepository


class SchedulePdfORM(Base):
    __tablename__ = "schedule_pdfs"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, nullable=False, index=True)  # ✅ DB réel
    title = Column(String(255), nullable=False)
    period = Column(String(50), nullable=True)
    file_path = Column(Text, nullable=False)
    uploaded_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class SqlAlchemyScheduleRepository(ScheduleRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        *,
        group_id: int,
        title: str,
        period: str | None,
        file_path: str,
        uploaded_by: int,
    ) -> SchedulePdf:
        row = SchedulePdfORM(
            group_id=group_id,
            title=title,
            period=period,
            file_path=file_path,
            uploaded_by=uploaded_by,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def get_latest_for_group(self, group_id: int) -> Optional[SchedulePdf]:
        row = (
            self.db.query(SchedulePdfORM)
            .filter(SchedulePdfORM.group_id == group_id)
            .order_by(desc(SchedulePdfORM.created_at))
            .first()
        )
        return self._to_domain(row) if row else None

    def get_by_id(self, schedule_id: int) -> Optional[SchedulePdf]:
        row = (
            self.db.query(SchedulePdfORM)
            .filter(SchedulePdfORM.id == schedule_id)
            .first()
        )
        return self._to_domain(row) if row else None

    def list_for_group(self, group_id: int) -> List[SchedulePdf]:
        rows = (
            self.db.query(SchedulePdfORM)
            .filter(SchedulePdfORM.group_id == group_id)
            .order_by(desc(SchedulePdfORM.created_at))
            .all()
        )
        return [self._to_domain(r) for r in rows]

    @staticmethod
    def _to_domain(row: SchedulePdfORM) -> SchedulePdf:
        return SchedulePdf(
            id=row.id,
            group_id=row.group_id,
            title=row.title,
            period=row.period,
            file_path=row.file_path,
            uploaded_by=row.uploaded_by,
            created_at=row.created_at,
        )
