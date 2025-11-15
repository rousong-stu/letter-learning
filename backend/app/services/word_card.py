from __future__ import annotations

from datetime import datetime
from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.repositories import user_word_book as user_word_book_repo

WordCardAction = Literal["too_easy", "know", "review"]


class WordCardError(RuntimeError):
    pass


async def list_learning_cards(
    session: AsyncSession,
    user: User,
    *,
    limit: int = 12,
):
    records = await user_word_book_repo.list_learning_words(session, user.id, limit)
    cards: list[dict] = []
    for entry_id, word, status, hits in records:
        cards.append(
            {
                "id": entry_id,
                "word": word,
                "mastery_status": status,
                "consecutive_known_hits": hits,
            }
        )
    return cards


async def apply_action(
    session: AsyncSession,
    user: User,
    *,
    entry_id: int,
    action: WordCardAction,
) -> dict:
    entry = await user_word_book_repo.get_entry_by_id(
        session, entry_id=entry_id, user_id=user.id
    )
    if not entry:
        raise WordCardError("单词不存在或已完成学习")

    now = datetime.utcnow()
    entry.last_studied_at = now
    entry.study_count = (entry.study_count or 0) + 1

    if action == "too_easy":
        entry.mastery_status = "mastered"
        entry.consecutive_known_hits = 0
    elif action == "know":
        entry.consecutive_known_hits = (entry.consecutive_known_hits or 0) + 1
        if entry.consecutive_known_hits >= 2:
            entry.mastery_status = "mastered"
            entry.consecutive_known_hits = 0
        else:
            entry.mastery_status = "learning"
    else:  # review related actions
        entry.consecutive_known_hits = 0
        entry.mastery_status = "learning"

    await session.flush()
    return {
        "id": entry.id,
        "word": entry.word.word if entry.word else "",
        "mastery_status": entry.mastery_status,
        "consecutive_known_hits": entry.consecutive_known_hits,
    }
