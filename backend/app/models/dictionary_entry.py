from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, DateTime, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.types import bigint


class DictionaryEntry(Base):
    """本地缓存的词典条目，避免重复调用外部 API。"""

    __tablename__ = "dictionary_entries"
    __table_args__ = (
        UniqueConstraint(
            "normalized_word",
            name="uq_dictionary_entries_normalized_word",
        ),
    )

    id: Mapped[int] = mapped_column(
        bigint(), primary_key=True, autoincrement=True, comment="主键"
    )
    word: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        comment="原始单词（保留大小写）",
    )
    normalized_word: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
        comment="标准化单词（小写）",
    )
    part_of_speech: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="词性"
    )
    phonetics: Mapped[list[dict]] = mapped_column(
        JSON, nullable=False, default=list, comment="音标与音频列表"
    )
    variants: Mapped[list[str]] = mapped_column(
        JSON, nullable=False, default=list, comment="变体拼写"
    )
    inflections: Mapped[list[str]] = mapped_column(
        JSON, nullable=False, default=list, comment="词形变化"
    )
    definitions: Mapped[list[dict]] = mapped_column(
        JSON, nullable=False, default=list, comment="释义与例句"
    )
    synonyms: Mapped[list[str]] = mapped_column(
        JSON, nullable=False, default=list, comment="同义词"
    )
    antonyms: Mapped[list[str]] = mapped_column(
        JSON, nullable=False, default=list, comment="反义词"
    )
    labels: Mapped[dict] = mapped_column(
        JSON, nullable=False, default=dict, comment="标签（general/usage 等）"
    )
    etymology: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="词源"
    )
    chinese_translation: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="中文释义"
    )
    source: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="数据来源（例如 Merriam-Webster）"
    )
    source_metadata: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="原始响应等额外数据"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="创建时间",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )

    def __repr__(self) -> str:
        return f"<DictionaryEntry word={self.word!r}>"
