from __future__ import annotations

from datetime import date, datetime
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import WordStory


async def get_by_user_and_date(
    session: AsyncSession, user_id: int, story_date: date
) -> WordStory | None:
    stmt = (
        select(WordStory)
        .where(WordStory.user_id == user_id, WordStory.story_date == story_date)
        .limit(1)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def list_stories(
    session: AsyncSession,
    user_id: int,
    *,
    limit: int = 30,
) -> Sequence[WordStory]:
    stmt = (
        select(WordStory)
        .where(WordStory.user_id == user_id)
        .order_by(WordStory.story_date.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def create_word_story(
    session: AsyncSession,
    *,
    user_id: int,
    story_date: date,
    words: list[str],
    story_text: str,
    generated_at: datetime,
    story_tokens: int | None,
    model_name: str | None,
    status: str,
    extra: dict | None,
) -> WordStory:
    record = WordStory(
        user_id=user_id,
        story_date=story_date,
        generated_at=generated_at,
        words=words,
        story_text=story_text,
        story_tokens=story_tokens,
        model_name=model_name,
        status=status,
        extra=extra,
    )
    session.add(record)
    await session.flush()
    return record


async def update_word_story(
    session: AsyncSession,
    story: WordStory,
    *,
    words: list[str],
    story_text: str,
    generated_at: datetime,
    story_tokens: int | None,
    model_name: str | None,
    status: str,
    extra: dict | None,
) -> WordStory:
    story.words = words
    story.story_text = story_text
    story.generated_at = generated_at
    story.story_tokens = story_tokens
    story.model_name = model_name
    story.status = status
    story.extra = extra
    await session.flush()
    return story
