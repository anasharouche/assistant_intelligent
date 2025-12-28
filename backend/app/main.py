import os
from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.cors import add_cors
from app.shared.exceptions import unhandled_exception_handler
from app.api.v1.router import router as v1_router

from app.db.base import Base
from app.db.session import engine

# ⚠️ IMPORT OBLIGATOIRE DES MODELES ORM
from app.modules.timetable.infrastructure.repositories import SchedulePdfORM


# Forcer UTF-8 partout
os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")


def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # CORS
    add_cors(app)

    # Exceptions globales
    app.add_exception_handler(Exception, unhandled_exception_handler)

    # Routes API
    app.include_router(v1_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()

# 🔥 CRÉATION DES TABLES AU DÉMARRAGE
Base.metadata.create_all(bind=engine)
