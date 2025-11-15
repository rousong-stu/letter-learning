"""create word book tables

Revision ID: 9c954c6d8f92
Revises: 5f02fe4dbf4d
Create Date: 2025-11-15 11:00:33.982782

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql


def bigint():
    base = sa.BigInteger()
    base = base.with_variant(sa.Integer(), "sqlite")
    base = base.with_variant(mysql.BIGINT(unsigned=True), "mysql")
    return base


# revision identifiers, used by Alembic.
revision = "9c954c6d8f92"
down_revision = "5f02fe4dbf4d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "word_books",
        sa.Column("id", bigint(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("cover_url", sa.String(length=512), nullable=True),
        sa.Column("language", sa.String(length=32), nullable=True),
        sa.Column("level", sa.String(length=32), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("total_words", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
            server_onupdate=sa.text("CURRENT_TIMESTAMP"),
        ),
    )

    op.create_table(
        "word_book_words",
        sa.Column("id", bigint(), primary_key=True, autoincrement=True),
        sa.Column("word_book_id", bigint(), nullable=False),
        sa.Column("word", sa.String(length=128), nullable=False),
        sa.Column("phonetic", sa.String(length=128), nullable=True),
        sa.Column("part_of_speech", sa.String(length=32), nullable=True),
        sa.Column("meaning_en", sa.Text(), nullable=True),
        sa.Column("meaning_zh", sa.Text(), nullable=True),
        sa.Column("example_en", sa.Text(), nullable=True),
        sa.Column("example_zh", sa.Text(), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
            server_onupdate=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["word_book_id"],
            ["word_books.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("word_book_id", "word", name="uq_word_book_words_book_word"),
    )
    op.create_index(
        "idx_word_book_words_book_id",
        "word_book_words",
        ["word_book_id"],
    )

    op.create_table(
        "user_word_books",
        sa.Column("id", bigint(), primary_key=True, autoincrement=True),
        sa.Column("user_id", bigint(), nullable=False),
        sa.Column("word_book_id", bigint(), nullable=False),
        sa.Column("course_code", sa.String(length=64), nullable=True),
        sa.Column("daily_quota", sa.Integer(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column(
            "status",
            sa.String(length=32),
            nullable=False,
            server_default=sa.text("'active'"),
        ),
        sa.Column(
            "total_days",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
            server_onupdate=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["word_book_id"],
            ["word_books.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("user_id", "word_book_id", name="uq_user_word_books_user_book"),
    )
    op.create_index(
        "idx_user_word_books_user_id",
        "user_word_books",
        ["user_id"],
    )
    op.create_index(
        "idx_user_word_books_word_book_id",
        "user_word_books",
        ["word_book_id"],
    )

    op.create_table(
        "user_word_book_words",
        sa.Column("id", bigint(), primary_key=True, autoincrement=True),
        sa.Column("user_word_book_id", bigint(), nullable=False),
        sa.Column("word_book_word_id", bigint(), nullable=False),
        sa.Column("day_index", sa.Integer(), nullable=False),
        sa.Column("sequence_in_day", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("study_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_studied_at", sa.DateTime(), nullable=True),
        sa.Column(
            "mastery_status",
            sa.String(length=16),
            nullable=False,
            server_default=sa.text("'unlearned'"),
        ),
        sa.Column("mastery_confidence", sa.Float(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
            server_onupdate=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["user_word_book_id"],
            ["user_word_books.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["word_book_word_id"],
            ["word_book_words.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "user_word_book_id",
            "word_book_word_id",
            name="uq_user_word_book_words_user_word",
        ),
    )
    op.create_index(
        "idx_user_word_book_words_user_book_id",
        "user_word_book_words",
        ["user_word_book_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "idx_user_word_book_words_user_book_id",
        table_name="user_word_book_words",
    )
    op.drop_table("user_word_book_words")
    op.drop_index(
        "idx_user_word_books_word_book_id",
        table_name="user_word_books",
    )
    op.drop_index(
        "idx_user_word_books_user_id",
        table_name="user_word_books",
    )
    op.drop_table("user_word_books")
    op.drop_index(
        "idx_word_book_words_book_id",
        table_name="word_book_words",
    )
    op.drop_table("word_book_words")
    op.drop_table("word_books")
