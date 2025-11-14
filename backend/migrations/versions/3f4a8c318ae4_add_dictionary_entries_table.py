"""add dictionary entries table

Revision ID: 3f4a8c318ae4
Revises: 1f5a408f0615
Create Date: 2025-02-17 12:00:00.000000

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
revision = "3f4a8c318ae4"
down_revision = "44f7b3616b8d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "dictionary_entries",
        sa.Column("id", bigint(), primary_key=True, autoincrement=True, comment="主键"),
        sa.Column(
            "word",
            sa.String(length=128),
            nullable=False,
            comment="原始单词",
        ),
        sa.Column(
            "normalized_word",
            sa.String(length=128),
            nullable=False,
            comment="小写单词，便于索引",
        ),
        sa.Column(
            "part_of_speech",
            sa.String(length=64),
            nullable=True,
            comment="词性",
        ),
        sa.Column("phonetics", sa.JSON(), nullable=False, comment="音标与音频列表"),
        sa.Column("variants", sa.JSON(), nullable=False, comment="变体拼写"),
        sa.Column("inflections", sa.JSON(), nullable=False, comment="词形变化"),
        sa.Column("definitions", sa.JSON(), nullable=False, comment="释义与例句"),
        sa.Column("synonyms", sa.JSON(), nullable=False, comment="同义词"),
        sa.Column("antonyms", sa.JSON(), nullable=False, comment="反义词"),
        sa.Column("labels", sa.JSON(), nullable=False, comment="标签"),
        sa.Column("etymology", sa.Text(), nullable=True, comment="词源"),
        sa.Column("chinese_translation", sa.Text(), nullable=True, comment="中文释义"),
        sa.Column(
            "source",
            sa.String(length=64),
            nullable=True,
            comment="数据来源",
        ),
        sa.Column("source_metadata", sa.JSON(), nullable=True, comment="原始响应"),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
            comment="创建时间",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
            server_onupdate=sa.text("CURRENT_TIMESTAMP"),
            comment="更新时间",
        ),
        sa.UniqueConstraint(
            "normalized_word",
            name="uq_dictionary_entries_normalized_word",
        ),
    )
    op.create_index(
        "idx_dictionary_entries_word",
        "dictionary_entries",
        ["word"],
    )
    op.create_index(
        "idx_dictionary_entries_normalized_word",
        "dictionary_entries",
        ["normalized_word"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "idx_dictionary_entries_normalized_word",
        table_name="dictionary_entries",
    )
    op.drop_index("idx_dictionary_entries_word", table_name="dictionary_entries")
    op.drop_table("dictionary_entries")
