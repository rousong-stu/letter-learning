from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    health,
    notice,
    profile,
    user_management,
    word_story,
)

router = APIRouter()
router.include_router(health.router, tags=["系统"])
router.include_router(auth.router, tags=["认证"])
router.include_router(user_management.router, tags=["用户管理"])
router.include_router(notice.router, tags=["公告"])
router.include_router(profile.router, tags=["个人中心"])
router.include_router(word_story.router, tags=["AI 词汇短文"])
