from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func, text

from app.models.base import Base
from app.models.types import bigint


class AiChatSession(Base):
    """AI 对话会话记录。"""

    __tablename__ = "ai_chat_sessions"

    id: Mapped[int] = mapped_column(
        bigint(), primary_key=True, autoincrement=True, comment="主键"
    )
    user_id: Mapped[int] = mapped_column(
        bigint(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="发起用户",
    )
    word_story_id: Mapped[int | None] = mapped_column(
        bigint(),
        ForeignKey("word_stories.id", ondelete="SET NULL"),
        nullable=True,
        comment="关联短文",
    )
    coze_conversation_id: Mapped[str | None] = mapped_column(
        String(128), nullable=True, comment="Coze conversation_id"
    )
    total_rounds: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
        comment="已经完成的轮数",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        server_default=text("'active'"),
        comment="active/completed",
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="开始时间"
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="结束时间"
    )
    extra: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment="额外信息")

    user: Mapped["User"] = relationship(
        "User", back_populates="ai_chat_sessions", lazy="joined"
    )
    word_story: Mapped[Optional["WordStory"]] = relationship(
        "WordStory", lazy="noload"
    )
    messages: Mapped[List["AiChatMessage"]] = relationship(
        "AiChatMessage",
        back_populates="chat",
        cascade="all, delete-orphan",
        order_by="AiChatMessage.sequence",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<AiChatSession id={self.id} user_id={self.user_id}>"


class AiChatMessage(Base):
    """AI 对话消息。"""

    __tablename__ = "ai_chat_messages"

    id: Mapped[int] = mapped_column(
        bigint(), primary_key=True, autoincrement=True, comment="主键"
    )
    chat_id: Mapped[int] = mapped_column(
        bigint(),
        ForeignKey("ai_chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="会话 ID",
    )
    sender: Mapped[str] = mapped_column(
        String(16), nullable=False, comment="user/ai"
    )
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="展示文案")
    payload: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, comment="额外数据"
    )
    sequence: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
        comment="排序序号",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="创建时间"
    )

    chat: Mapped["AiChatSession"] = relationship(
        "AiChatSession", back_populates="messages"
    )

    def __repr__(self) -> str:
        return f"<AiChatMessage chat_id={self.chat_id} sender={self.sender}>"
