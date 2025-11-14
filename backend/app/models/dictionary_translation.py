from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.types import bigint


class DictionaryDefinitionTranslation(Base):
    """单词释义对应的中文翻译缓存。"""

    __tablename__ = "dictionary_definition_translations"
    __table_args__ = (
        UniqueConstraint(
            "dictionary_entry_id",
            "definition_index",
            name="uq_dictionary_definition_translations_entry_index",
        ),
    )

    id: Mapped[int] = mapped_column(
        bigint(), primary_key=True, autoincrement=True, comment="主键"
    )
    dictionary_entry_id: Mapped[int] = mapped_column(
        bigint(),
        ForeignKey("dictionary_entries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="关联的词典条目",
    )
    definition_index: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="释义索引（从 0 开始）"
    )
    translation: Mapped[str] = mapped_column(
        Text, nullable=False, comment="中文释义"
    )
    source: Mapped[str | None] = mapped_column(
        String(64), nullable=True, comment="生成来源（AI 模型、人工等）"
    )
    metadata_json: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, comment="额外元数据"
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

    entry: Mapped["DictionaryEntry"] = relationship(
        "DictionaryEntry", back_populates="translations", lazy="joined"
    )

    def __repr__(self) -> str:
        return (
            f"<DictionaryDefinitionTranslation entry={self.dictionary_entry_id} "
            f"index={self.definition_index}>"
        )
