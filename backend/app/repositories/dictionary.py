from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DictionaryEntry


async def get_by_normalized_word(
    session: AsyncSession, normalized_word: str
) -> DictionaryEntry | None:
    stmt = (
        select(DictionaryEntry)
        .options(selectinload(DictionaryEntry.translations))
        .where(DictionaryEntry.normalized_word == normalized_word)
        .limit(1)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_by_id(session: AsyncSession, entry_id: int) -> DictionaryEntry | None:
    stmt = (
        select(DictionaryEntry)
        .options(selectinload(DictionaryEntry.translations))
        .where(DictionaryEntry.id == entry_id)
        .limit(1)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_entry(
    session: AsyncSession,
    *,
    word: str,
    normalized_word: str,
    part_of_speech: str | None,
    phonetics: list[dict],
    variants: list[str],
    inflections: list[str],
    definitions: list[dict],
    synonyms: list[str],
    antonyms: list[str],
    labels: dict,
    etymology: str | None,
    chinese_translation: str | None,
    source: str | None,
    source_metadata: dict | None,
) -> DictionaryEntry:
    record = DictionaryEntry(
        word=word,
        normalized_word=normalized_word,
        part_of_speech=part_of_speech,
        phonetics=phonetics,
        variants=variants,
        inflections=inflections,
        definitions=definitions,
        synonyms=synonyms,
        antonyms=antonyms,
        labels=labels,
        etymology=etymology,
        chinese_translation=chinese_translation,
        source=source,
        source_metadata=source_metadata,
    )
    session.add(record)
    await session.flush()
    await session.refresh(record)
    return record
