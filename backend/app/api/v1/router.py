from fastapi import APIRouter

from app.api.v1.endpoints import auth, health

router = APIRouter()
router.include_router(health.router, tags=["系统"])
router.include_router(auth.router, tags=["认证"])
