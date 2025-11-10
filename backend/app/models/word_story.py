from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    JSON,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base
from app.models.types import bigint


class WordStory(Base):
    """每日 AI 词汇短文记录。"""

    __tablename__ = "word_stories"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "story_date",
            name="uq_word_stories_user_story_date",
        ),
    )

    id: Mapped[int] = mapped_column(
        bigint(), primary_key=True, autoincrement=True, comment="主键"
    )
    user_id: Mapped[int] = mapped_column(
        bigint(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="生成用户",
    )
    story_date: Mapped[date] = mapped_column(
        Date, nullable=False, comment="学习日期"
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="生成时间",
    )
    words: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        comment="词汇数组",
    )
    story_text: Mapped[str] = mapped_column(
        Text, nullable=False, comment="AI 生成短文"
    )
    story_tokens: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="token 消耗"
    )
    model_name: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True, comment="模型/智能体"
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        server_default=text("'success'"),
        comment="生成状态",
    )
    extra: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="额外元数据"
    )

    user: Mapped["User"] = relationship(
        "User", back_populates="word_stories", lazy="joined"
    )

    def __repr__(self) -> str:
        return f"<WordStory user_id={self.user_id} date={self.story_date}>"
