from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.word_book import WordBook


async def list_published_books(session: AsyncSession) -> list[WordBook]:
    stmt = (
        select(WordBook)
        .where(WordBook.is_published.is_(True))
        .order_by(WordBook.created_at.desc())
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_book_with_words(
    session: AsyncSession, book_id: int
) -> WordBook | None:
    stmt = (
        select(WordBook)
        .options(selectinload(WordBook.words))
        .where(WordBook.id == book_id, WordBook.is_published.is_(True))
        .limit(1)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

