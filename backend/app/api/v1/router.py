from fastapi import APIRouter

from app.api.v1.endpoints import (
    ai_chat,
    auth,
    dictionary,
    health,
    notice,
    profile,
    user_management,
    user_word_book,
    word_book,
    word_card,
    word_story,
)

router = APIRouter()
router.include_router(health.router, tags=["系统"])
router.include_router(auth.router, tags=["认证"])
router.include_router(user_management.router, tags=["用户管理"])
router.include_router(notice.router, tags=["公告"])
router.include_router(profile.router, tags=["个人中心"])
router.include_router(word_story.router, tags=["AI 词汇短文"])
router.include_router(dictionary.router, tags=["词典"])
router.include_router(word_book.router, tags=["单词书"])
router.include_router(user_word_book.router, tags=["用户单词书"])
router.include_router(ai_chat.router, tags=["AI 对话"])
router.include_router(word_card.router, tags=["单词卡片"])
