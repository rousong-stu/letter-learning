from __future__ import annotations

from datetime import datetime

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator


class WordBookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None = None
    cover_url: str | None = None
    language: str | None = None
    level: str | None = None
    tags: list[str] = []
    total_words: int
    is_published: bool
    created_at: datetime
    updated_at: datetime


class WordBookListResponse(BaseModel):
    items: list[WordBookResponse]


class LearningPlanRequest(BaseModel):
    word_book_id: int
    daily_quota: int = Field(ge=5, le=40)
    course_code: str | None = None
    start_date: date
    enable_reminder: bool = False
    notes: str | None = None
    reset: bool = False

    @field_validator("start_date")
    @classmethod
    def start_date_not_past(cls, value: date) -> date:
        if value < date.today():
            raise ValueError("开始日期不能早于今天")
        return value


class LearningPlanResponse(BaseModel):
    id: int
    word_book_id: int
    daily_quota: int
    course_code: str | None = None
    start_date: date
    total_days: int


class CurrentLearningPlanResponse(BaseModel):
    id: int
    word_book: WordBookResponse
    daily_quota: int
    course_code: str | None
    start_date: date
    total_days: int
