from __future__ import annotations

from datetime import datetime, date

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
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


class WordBook(Base):
    """系统维护的单词书。"""

    __tablename__ = "word_books"

    id: Mapped[int] = mapped_column(
        bigint(), primary_key=True, autoincrement=True, comment="主键"
    )
    title: Mapped[str] = mapped_column(String(128), nullable=False, comment="单词书名称")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="描述")
    cover_url: Mapped[str | None] = mapped_column(
        String(512), nullable=True, comment="封面图片 URL"
    )
    language: Mapped[str | None] = mapped_column(
        String(32), nullable=True, comment="语言（如 en）"
    )
    level: Mapped[str | None] = mapped_column(
        String(32), nullable=True, comment="水平（如 CET4、TOEFL）"
    )
    tags: Mapped[list[str]] = mapped_column(
        JSON, nullable=False, default=list, comment="标签"
    )
    total_words: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="单词数"
    )
    is_published: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="是否发布"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )

    words: Mapped[list["WordBookWord"]] = relationship(
        "WordBookWord", back_populates="book", cascade="all, delete-orphan"
    )
    user_books: Mapped[list["UserWordBook"]] = relationship(
        "UserWordBook", back_populates="book", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<WordBook id={self.id} title={self.title!r}>"


class WordBookWord(Base):
    """单词书内的单词条目。"""

    __tablename__ = "word_book_words"
    __table_args__ = (
        UniqueConstraint(
            "word_book_id",
            "word",
            name="uq_word_book_words_book_word",
        ),
    )

    id: Mapped[int] = mapped_column(
        bigint(), primary_key=True, autoincrement=True, comment="主键"
    )
    word_book_id: Mapped[int] = mapped_column(
        bigint(),
        ForeignKey("word_books.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="所在单词书",
    )
    word: Mapped[str] = mapped_column(String(128), nullable=False, comment="单词")
    phonetic: Mapped[str | None] = mapped_column(
        String(128), nullable=True, comment="音标"
    )
    part_of_speech: Mapped[str | None] = mapped_column(
        String(32), nullable=True, comment="词性"
    )
    meaning_en: Mapped[str | None] = mapped_column(Text, nullable=True, comment="英文释义")
    meaning_zh: Mapped[str | None] = mapped_column(Text, nullable=True, comment="中文释义")
    example_en: Mapped[str | None] = mapped_column(Text, nullable=True, comment="英文例句")
    example_zh: Mapped[str | None] = mapped_column(Text, nullable=True, comment="中文例句")
    order_index: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="原书顺序"
    )
    metadata_json: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, comment="额外元数据"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )

    book: Mapped["WordBook"] = relationship("WordBook", back_populates="words")

    def __repr__(self) -> str:
        return f"<WordBookWord book_id={self.word_book_id} word={self.word!r}>"


class UserWordBook(Base):
    """用户选择的单词书（学习计划）。"""

    __tablename__ = "user_word_books"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "word_book_id",
            name="uq_user_word_books_user_book",
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
        comment="用户 ID",
    )
    word_book_id: Mapped[int] = mapped_column(
        bigint(),
        ForeignKey("word_books.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="单词书 ID",
    )
    course_code: Mapped[str | None] = mapped_column(
        String(64), nullable=True, comment="学习课程（可选）"
    )
    daily_quota: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="每日学习单词数"
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False, comment="开始日期")
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="active",
        comment="状态：active/completed/paused",
    )
    total_days: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="总学习天数"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )

    book: Mapped["WordBook"] = relationship("WordBook", back_populates="user_books")
    words: Mapped[list["UserWordBookWord"]] = relationship(
        "UserWordBookWord",
        back_populates="user_book",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<UserWordBook user_id={self.user_id} book_id={self.word_book_id}>"


class UserWordBookWord(Base):
    """用户词表（包含学习进度信息）。"""

    __tablename__ = "user_word_book_words"
    __table_args__ = (
        UniqueConstraint(
            "user_word_book_id",
            "word_book_word_id",
            name="uq_user_word_book_words_user_word",
        ),
    )

    id: Mapped[int] = mapped_column(
        bigint(), primary_key=True, autoincrement=True, comment="主键"
    )
    user_word_book_id: Mapped[int] = mapped_column(
        bigint(),
        ForeignKey("user_word_books.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="所属用户单词书",
    )
    word_book_word_id: Mapped[int] = mapped_column(
        bigint(),
        ForeignKey("word_book_words.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="关联的系统单词",
    )
    day_index: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Day 序号（从 1 开始）"
    )
    sequence_in_day: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="日内顺序"
    )
    study_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="学习次数"
    )
    last_studied_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="最后学习时间"
    )
    mastery_status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="unlearned",
        comment="掌握状态：unlearned/learning/mastered",
    )
    mastery_confidence: Mapped[float | None] = mapped_column(
        Integer, nullable=True, comment="掌握评分"
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )

    user_book: Mapped["UserWordBook"] = relationship("UserWordBook", back_populates="words")
    word: Mapped["WordBookWord"] = relationship("WordBookWord")

    def __repr__(self) -> str:
        return f"<UserWordBookWord user_book={self.user_word_book_id} word={self.word_book_word_id}>"
