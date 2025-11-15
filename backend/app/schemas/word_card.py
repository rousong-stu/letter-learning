from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class WordCardItem(BaseModel):
    id: int
    word: str
    mastery_status: str
    consecutive_known_hits: int


class WordCardListResponse(BaseModel):
    items: list[WordCardItem]


class WordCardActionRequest(BaseModel):
    action: Literal["too_easy", "know", "review"] = Field(..., description="操作类型")


class WordCardActionResponse(BaseModel):
    item: WordCardItem
