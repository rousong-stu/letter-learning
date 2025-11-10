"""add word stories table

Revision ID: 1f5a408f0615
Revises: 7a8c11cbc48c
Create Date: 2025-11-10 14:35:00.000000

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
revision = "1f5a408f0615"
down_revision = "7a8c11cbc48c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "word_stories",
        sa.Column("id", bigint(), primary_key=True, autoincrement=True, comment="主键"),
        sa.Column(
            "user_id",
            bigint(),
            nullable=False,
            comment="生成用户",
        ),
        sa.Column("story_date", sa.Date(), nullable=False, comment="学习日期"),
        sa.Column(
            "generated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
            comment="生成时间",
        ),
        sa.Column("words", sa.JSON(), nullable=False, comment="词汇数组"),
        sa.Column("story_text", sa.Text(), nullable=False, comment="AI 生成短文"),
        sa.Column("story_tokens", sa.Integer(), nullable=True, comment="token 消耗"),
        sa.Column(
            "model_name",
            sa.String(length=128),
            nullable=True,
            comment="模型/智能体",
        ),
        sa.Column(
            "status",
            sa.String(length=32),
            nullable=False,
            server_default=sa.text("'success'"),
            comment="生成状态",
        ),
        sa.Column("extra", sa.JSON(), nullable=True, comment="额外元数据"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint(
            "user_id",
            "story_date",
            name="uq_word_stories_user_story_date",
        ),
    )
    op.create_index(
        "idx_word_stories_user_id",
        "word_stories",
        ["user_id"],
    )
    op.create_index(
        "idx_word_stories_story_date",
        "word_stories",
        ["story_date"],
    )


def downgrade() -> None:
    op.drop_index("idx_word_stories_story_date", table_name="word_stories")
    op.drop_index("idx_word_stories_user_id", table_name="word_stories")
    op.drop_table("word_stories")
