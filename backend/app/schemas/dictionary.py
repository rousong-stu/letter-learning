from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class PhoneticSchema(BaseModel):
    notation: str | None = None
    audio_url: str | None = None


class DefinitionSchema(BaseModel):
    meaning: str
    examples: list[str] = []
    translation: str | None = None


class LabelSchema(BaseModel):
    general: list[str] = []
    usage: list[str] = []
    parenthetical: list[str] = []


class DictionaryEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    word: str
    normalized_word: str
    part_of_speech: str | None = None
    phonetics: list[PhoneticSchema] = []
    variants: list[str] = []
    inflections: list[str] = []
    definitions: list[DefinitionSchema] = []
    synonyms: list[str] = []
    antonyms: list[str] = []
    labels: LabelSchema = LabelSchema()
    etymology: str | None = None
    chinese_translation: str | None = None
    source: str | None = None
    created_at: datetime
    updated_at: datetime


class DefinitionTranslationRequest(BaseModel):
    force: bool = False


class DefinitionTranslationResponse(BaseModel):
    dictionary_entry_id: int
    definition_index: int
    translation: str
