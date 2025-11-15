from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.word_book import (
    UserWordBook,
    UserWordBookWord,
    WordBookWord,
)


async def get_by_user_and_book(
    session: AsyncSession, user_id: int, word_book_id: int
) -> UserWordBook | None:
    stmt = (
        select(UserWordBook)
        .options(selectinload(UserWordBook.words))
        .where(
            UserWordBook.user_id == user_id,
            UserWordBook.word_book_id == word_book_id,
        )
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_latest_by_user(
    session: AsyncSession, user_id: int
) -> UserWordBook | None:
    stmt = (
        select(UserWordBook)
        .options(selectinload(UserWordBook.book))
        .where(UserWordBook.user_id == user_id)
        .order_by(UserWordBook.created_at.desc())
        .limit(1)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def list_words_for_day(
    session: AsyncSession,
    user_word_book_id: int,
    day_index: int,
    daily_quota: int,
) -> list[str]:
    stmt = (
        select(WordBookWord.word)
        .join(
            UserWordBookWord,
            UserWordBookWord.word_book_word_id == WordBookWord.id,
        )
        .where(
            UserWordBookWord.user_word_book_id == user_word_book_id,
            UserWordBookWord.day_index == day_index,
        )
        .order_by(
            UserWordBookWord.sequence_in_day.asc(),
            WordBookWord.id.asc(),
        )
    )
    result = await session.execute(stmt)
    words = [row[0] for row in result.fetchall() if row and row[0]]
    if words:
        return words

    fallback_stmt = (
        select(WordBookWord.word)
        .join(
            UserWordBookWord,
            UserWordBookWord.word_book_word_id == WordBookWord.id,
        )
        .where(UserWordBookWord.user_word_book_id == user_word_book_id)
        .order_by(
            UserWordBookWord.day_index.asc(),
            UserWordBookWord.sequence_in_day.asc(),
            WordBookWord.id.asc(),
        )
        .limit(daily_quota)
    )
    result = await session.execute(fallback_stmt)
    return [row[0] for row in result.fetchall() if row and row[0]]


async def create_user_word_book(
    session: AsyncSession,
    *,
    user_id: int,
    word_book_id: int,
    daily_quota: int,
    course_code: str | None,
    start_date,
    total_days: int,
) -> UserWordBook:
    record = UserWordBook(
        user_id=user_id,
        word_book_id=word_book_id,
        daily_quota=daily_quota,
        course_code=course_code,
        start_date=start_date,
        total_days=total_days,
        status="active",
    )
    session.add(record)
    await session.flush()
    return record


async def delete_by_user(session: AsyncSession, user_id: int) -> None:
    await session.execute(delete(UserWordBook).where(UserWordBook.user_id == user_id))
    await session.flush()
