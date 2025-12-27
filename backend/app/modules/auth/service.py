from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password, create_access_token
from app.db.repositories.user_repo import get_user_by_email, create_user

ALLOWED_ROLES = {"STUDENT", "TEACHER", "SCOLARITE", "ADMIN"}


# =====================
# REGISTER
# =====================
def register(db: Session, email: str, password: str, role: str):
    if role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid role"
        )

    existing = get_user_by_email(db, email)
    if existing:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    user = create_user(
        db,
        email=email,
        hashed_password=hash_password(password),
        role=role,
    )

    # ✅ JWT basé sur l'email (logique cohérente)
    token = create_access_token(
        email=user.email,
        role=user.role
    )

    return user, token


# =====================
# LOGIN
# =====================
def login(db: Session, email: str, password: str) -> str:
    user = get_user_by_email(db, email)

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Inactive user"
        )

    # ✅ JWT basé sur l'email
    token = create_access_token(
        email=user.email,
        role=user.role
    )

    return token
