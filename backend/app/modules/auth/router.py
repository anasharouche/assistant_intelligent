from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.modules.auth.schemas import RegisterIn, LoginIn, TokenOut, MeOut
from app.modules.auth.service import register as register_service, login as login_service
from app.modules.auth.deps import get_current_user
from app.shared.responses import ApiResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=ApiResponse[TokenOut])
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    user, token = register_service(db, payload.email, payload.password, payload.role)
    return ApiResponse(data=TokenOut(access_token=token))


@router.post("/login")
def login_user(payload: LoginIn, db: Session = Depends(get_db)):
    token = login_service(db, payload.email, payload.password)

    return {
        "data": {
            "access_token": token,
            "token_type": "bearer"
        },
        "meta": {
            "request_id": None
        },
        "error": None
    }


@router.get("/me", response_model=ApiResponse[MeOut])
def me(user=Depends(get_current_user)):
    return ApiResponse(
        data=MeOut(
            id=user.id,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
        )
    )
