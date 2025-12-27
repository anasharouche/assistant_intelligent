from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

# =====================
# SQLALCHEMY ENGINE
# =====================
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)

# =====================
# SESSION FACTORY
# =====================
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# =====================
# DEPENDENCY
# =====================
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
