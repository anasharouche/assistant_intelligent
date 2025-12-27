from datetime import date, time
from pydantic import BaseModel


class ModuleOut(BaseModel):
    id: int
    code: str
    name: str
    niveau: str
    filiere_id: int


class TimetableSessionOut(BaseModel):
    id: int
    date: date
    start_time: time
    end_time: time
    room: str
    module_id: int
    groupe_id: int
    teacher_id: int
