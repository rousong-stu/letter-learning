from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AiChatMessageSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sender: Literal["ai", "user"]
    content: str
    sequence: int
    created_at: datetime


class AiChatSessionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    word_story_id: int | None
    total_rounds: int
    status: str
    started_at: datetime
    ended_at: datetime | None


class AiChatSessionCreateRequest(BaseModel):
    story_text: str = Field("", description="当前短文内容", max_length=20000)
    word_story_id: int | None = Field(
        default=None, description="关联的短文 ID，可选"
    )


class AiChatSessionDetailResponse(BaseModel):
    session: AiChatSessionSchema
    messages: list[AiChatMessageSchema]


class AiChatSendMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000, description="提问内容")


class AiChatSendMessageResponse(BaseModel):
    session: AiChatSessionSchema
    new_messages: list[AiChatMessageSchema]
