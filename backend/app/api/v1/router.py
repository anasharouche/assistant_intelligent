from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.modules.auth.router import router as auth_router
from app.modules.scolarite.router import router as scolarite_router
from app.modules.documents.router import router as documents_router
from app.modules.rag.api.router import router as rag_router






router = APIRouter()
router.include_router(health_router)
router.include_router(auth_router)
router.include_router(scolarite_router)
router.include_router(documents_router)
router.include_router(rag_router)