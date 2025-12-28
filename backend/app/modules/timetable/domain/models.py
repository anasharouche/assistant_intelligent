from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class SchedulePdf:
    """
    Emploi du temps PDF associé à un groupe.
    """
    id: int
    group_id: int
    title: str
    period: Optional[str]          # ex: "S1", "S2", "2025-W03"
    file_path: str                # chemin local storage/...
    uploaded_by: int              # user_id (scolarité)
    created_at: datetime
