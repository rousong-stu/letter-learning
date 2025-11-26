from __future__ import annotations

from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import AiChatMessage, User, WordStory, UserWordBook, UserWordBookWord, WordBook
from app.utils.response import success_response

router = APIRouter(prefix="/dashboard")


@router.get("/summary")
async def dashboard_summary(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_id = current_user.id

    # 已学习单词（任意学习次数 > 0）
    studied_stmt = select(func.count()).select_from(UserWordBookWord).where(
        UserWordBookWord.study_count > 0,
        UserWordBookWord.user_word_book_id.in_(
            select(UserWordBook.id).where(UserWordBook.user_id == user_id)
        ),
    )
    studied_count = (await session.execute(studied_stmt)).scalar_one()

    # 已掌握单词（用于计算达成度）
    mastered_stmt = select(func.count()).select_from(UserWordBookWord).where(
        UserWordBookWord.mastery_status == "mastered",
        UserWordBookWord.user_word_book_id.in_(
            select(UserWordBook.id).where(UserWordBook.user_id == user_id)
        ),
    )
    mastered_count = (await session.execute(mastered_stmt)).scalar_one()

    # 当前计划总词数
    total_words_stmt = (
        select(func.coalesce(func.sum(WordBook.total_words), 0))
        .select_from(UserWordBook)
        .join(WordBook, UserWordBook.word_book_id == WordBook.id)
        .where(UserWordBook.user_id == user_id)
    )
    total_words = (await session.execute(total_words_stmt)).scalar_one()

    # 总聊天轮次：仅统计用户发送的消息数
    chat_stmt = select(func.count()).select_from(AiChatMessage).where(
        AiChatMessage.chat.has(user_id=user_id),
        AiChatMessage.sender == "user",
    )
    chat_rounds = (await session.execute(chat_stmt)).scalar_one()

    # 总学习文章
    story_stmt = select(func.count()).select_from(WordStory).where(
        WordStory.user_id == user_id
    )
    story_count = (await session.execute(story_stmt)).scalar_one()

    completion_rate = 0.0
    if total_words:
        completion_rate = round(mastered_count / total_words * 100, 2)

    # 对话趋势（最近 7 天）
    start_day = date.today() - timedelta(days=6)
    chat_trends_stmt = (
        select(func.date(AiChatMessage.created_at), func.count())
        .where(AiChatMessage.chat.has(user_id=user_id))
        .where(AiChatMessage.sender == "user")
        .where(func.date(AiChatMessage.created_at) >= start_day)
        .group_by(func.date(AiChatMessage.created_at))
        .order_by(func.date(AiChatMessage.created_at))
    )
    chat_trends = [
        {"date": str(row[0]), "count": row[1]}
        for row in (await session.execute(chat_trends_stmt)).all()
    ]

    # 记忆曲线（用已掌握累计/总词数的简单模拟）
    memory_curve: list[dict[str, str | int]] = []
    for i in range(6, -1, -1):
        d = date.today() - timedelta(days=i)
        progress = (
            int(completion_rate) + (i - 3)  # 小幅波动
            if completion_rate
            else 0
        )
        progress = max(0, min(100, progress))
        memory_curve.append({"date": str(d), "rate": progress})

    data = {
        "summary": {
            "total_words_learned": studied_count,
            "total_chat_rounds": chat_rounds,
            "total_stories": story_count,
            "completion_rate": completion_rate,
            "total_words": total_words,
        },
        "chat_trends": chat_trends,
        "memory_curve": memory_curve,
    }
    return success_response(data)
