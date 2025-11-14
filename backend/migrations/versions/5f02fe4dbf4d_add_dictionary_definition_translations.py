"""add dictionary definition translations table

Revision ID: 5f02fe4dbf4d
Revises: 3f4a8c318ae4
Create Date: 2025-11-15 01:32:24.203235

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
revision = "5f02fe4dbf4d"
down_revision = "3f4a8c318ae4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "dictionary_definition_translations",
        sa.Column("id", bigint(), primary_key=True, autoincrement=True, comment="主键"),
        sa.Column(
            "dictionary_entry_id",
            bigint(),
            nullable=False,
            comment="词典条目",
        ),
        sa.Column(
            "definition_index",
            sa.Integer(),
            nullable=False,
            comment="释义索引（从0开始）",
        ),
        sa.Column("translation", sa.Text(), nullable=False, comment="中文释义"),
        sa.Column("source", sa.String(length=64), nullable=True, comment="来源"),
        sa.Column("metadata_json", sa.JSON(), nullable=True, comment="额外元数据"),
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
            ["dictionary_entry_id"],
            ["dictionary_entries.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "dictionary_entry_id",
            "definition_index",
            name="uq_dictionary_definition_translations_entry_index",
        ),
    )
    op.create_index(
        "idx_dictionary_definition_translations_entry_id",
        "dictionary_definition_translations",
        ["dictionary_entry_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "idx_dictionary_definition_translations_entry_id",
        table_name="dictionary_definition_translations",
    )
    op.drop_table("dictionary_definition_translations")
