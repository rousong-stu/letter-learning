from __future__ import annotations

from datetime import date, datetime
from typing import List

from pydantic import BaseModel, Field, ConfigDict


class WordStoryGenerateRequest(BaseModel):
    # 放宽校验，避免前端传参偶发 422
    words: List[str] | None = None
    story_date: date | None = None
    force: bool = False
    allow_exceed: bool = False

    model_config = ConfigDict(populate_by_name=True, extra="allow")


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
    extra: dict | None = None


class WordStoryListResponse(BaseModel):
    items: List[WordStoryResponse]
