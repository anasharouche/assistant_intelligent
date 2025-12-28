from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class StudentContext:
    user_id: int
    group_id: int


def can_access_schedule(student: StudentContext, schedule_group_id: int) -> bool:
    """
    Règle métier:
    Un étudiant ne peut accéder à un emploi du temps que si son group_id == schedule.group_id
    """
    return student.group_id == schedule_group_id
