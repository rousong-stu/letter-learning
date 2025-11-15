from __future__ import annotations

from datetime import date, datetime
from typing import List

from pydantic import BaseModel, Field, ConfigDict


class WordStoryGenerateRequest(BaseModel):
    words: List[str] | None = Field(default=None, max_items=100)
    story_date: date | None = None
    force: bool = False


class WordStoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, json_encoders={date: lambda v: v.isoformat()})

    id: int
    story_date: date = Field(serialization_alias="story_date")
    generated_at: datetime
    words: List[str]
    story_text: str
    story_tokens: int | None = None
    model_name: str | None = None
    image_url: str | None = None
    image_caption: str | None = None


class WordStoryListResponse(BaseModel):
    items: List[WordStoryResponse]
