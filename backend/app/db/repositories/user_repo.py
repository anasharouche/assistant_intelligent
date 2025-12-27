from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models.user import User


def get_user_by_email(db: Session, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    return db.execute(stmt).scalars().first()


def create_user(db: Session, email: str, hashed_password: str, role: str) -> User:
    user = User(email=email, hashed_password=hashed_password, role=role, is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
