from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dictionary_translation import DictionaryDefinitionTranslation


async def get_by_entry_and_index(
    session: AsyncSession, entry_id: int, definition_index: int
) -> DictionaryDefinitionTranslation | None:
    stmt = (
        select(DictionaryDefinitionTranslation)
        .where(
            DictionaryDefinitionTranslation.dictionary_entry_id == entry_id,
            DictionaryDefinitionTranslation.definition_index == definition_index,
        )
        .limit(1)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def upsert_translation(
    session: AsyncSession,
    *,
    entry_id: int,
    definition_index: int,
    translation: str,
    source: str | None,
    metadata: dict | None = None,
) -> DictionaryDefinitionTranslation:
    record = await get_by_entry_and_index(session, entry_id, definition_index)
    if record:
        record.translation = translation
        record.source = source
        record.metadata_json = metadata
    else:
        record = DictionaryDefinitionTranslation(
            dictionary_entry_id=entry_id,
            definition_index=definition_index,
            translation=translation,
            source=source,
            metadata_json=metadata,
        )
        session.add(record)
    await session.flush()
    await session.refresh(record)
    return record
