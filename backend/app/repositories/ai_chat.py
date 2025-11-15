from __future__ import annotations

from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AiChatMessage, AiChatSession


async def create_session(
    session: AsyncSession,
    *,
    user_id: int,
    word_story_id: int | None,
    extra: dict | None,
) -> AiChatSession:
    record = AiChatSession(
        user_id=user_id,
        word_story_id=word_story_id,
        extra=extra,
    )
    session.add(record)
    await session.flush()
    await session.refresh(record)
    return record


async def get_by_id(
    session: AsyncSession, chat_id: int, user_id: int
) -> AiChatSession | None:
    stmt = (
        select(AiChatSession)
        .where(AiChatSession.id == chat_id, AiChatSession.user_id == user_id)
        .limit(1)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def list_messages(
    session: AsyncSession, chat_id: int
) -> Sequence[AiChatMessage]:
    stmt = (
        select(AiChatMessage)
        .where(AiChatMessage.chat_id == chat_id)
        .order_by(AiChatMessage.sequence.asc())
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def append_message(
    session: AsyncSession,
    *,
    chat_id: int,
    sender: str,
    content: str,
    payload: dict | None,
) -> AiChatMessage:
    stmt = select(func.max(AiChatMessage.sequence)).where(
        AiChatMessage.chat_id == chat_id
    )
    result = await session.execute(stmt)
    max_sequence = result.scalar_one_or_none()
    next_sequence = (max_sequence if max_sequence is not None else -1) + 1

    message = AiChatMessage(
        chat_id=chat_id,
        sender=sender,
        content=content,
        payload=payload,
        sequence=next_sequence,
    )
    session.add(message)
    await session.flush()
    await session.refresh(message)
    return message
