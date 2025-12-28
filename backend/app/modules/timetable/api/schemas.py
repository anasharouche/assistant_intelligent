from __future__ import annotations
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ScheduleOut(BaseModel):
    id: int
    group_id: int
    title: str
    period: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UploadScheduleMetaIn(BaseModel):
    group_id: int
    title: str
    period: Optional[str] = None
