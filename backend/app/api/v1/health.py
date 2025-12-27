from fastapi import APIRouter
from pydantic import BaseModel
from app.shared.responses import ApiResponse
from sqlalchemy import text
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.deps import get_db


router = APIRouter(tags=["Health"])


class HealthOut(BaseModel):
    status: str
    service: str


@router.get("/health", response_model=ApiResponse[HealthOut])
def healthcheck():
    return ApiResponse(
        data=HealthOut(status="ok", service="assistant-scolarite-backend"),
        meta={"request_id": None},
    )
@router.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "db ok"}
