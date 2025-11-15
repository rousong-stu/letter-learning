"""add ai chat tables

Revision ID: 7c6d4a5c4635
Revises: b6b25e41ce09
Create Date: 2025-11-15 19:00:00.000000

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
revision = "7c6d4a5c4635"
down_revision = "b6b25e41ce09"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_chat_sessions",
        sa.Column("id", bigint(), primary_key=True, autoincrement=True, comment="主键"),
        sa.Column("user_id", bigint(), nullable=False, comment="用户 ID"),
        sa.Column(
            "word_story_id",
            bigint(),
            nullable=True,
            comment="关联短文",
        ),
        sa.Column(
            "coze_conversation_id",
            sa.String(length=128),
            nullable=True,
            comment="Coze 会话 ID",
        ),
        sa.Column(
            "total_rounds",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
            comment="已进行轮数",
        ),
        sa.Column(
            "status",
            sa.String(length=32),
            nullable=False,
            server_default=sa.text("'active'"),
            comment="状态",
        ),
        sa.Column(
            "started_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            comment="开始时间",
        ),
        sa.Column(
            "ended_at",
            sa.DateTime(),
            nullable=True,
            comment="结束时间",
        ),
        sa.Column("extra", sa.JSON(), nullable=True, comment="额外信息"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["word_story_id"], ["word_stories.id"], ondelete="SET NULL"
        ),
    )
    op.create_index(
        "idx_ai_chat_sessions_user_id",
        "ai_chat_sessions",
        ["user_id"],
    )

    op.create_table(
        "ai_chat_messages",
        sa.Column("id", bigint(), primary_key=True, autoincrement=True, comment="主键"),
        sa.Column("chat_id", bigint(), nullable=False, comment="会话 ID"),
        sa.Column(
            "sender",
            sa.String(length=16),
            nullable=False,
            comment="ai / user",
        ),
        sa.Column("content", sa.Text(), nullable=False, comment="消息内容"),
        sa.Column("payload", sa.JSON(), nullable=True, comment="额外数据"),
        sa.Column(
            "sequence",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
            comment="会话内顺序",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            comment="创建时间",
        ),
        sa.ForeignKeyConstraint(
            ["chat_id"], ["ai_chat_sessions.id"], ondelete="CASCADE"
        ),
        sa.UniqueConstraint("chat_id", "sequence", name="uq_ai_chat_messages_sequence"),
    )
    op.create_index(
        "idx_ai_chat_messages_chat_id",
        "ai_chat_messages",
        ["chat_id"],
    )


def downgrade() -> None:
    op.drop_index("idx_ai_chat_messages_chat_id", table_name="ai_chat_messages")
    op.drop_table("ai_chat_messages")
    op.drop_index("idx_ai_chat_sessions_user_id", table_name="ai_chat_sessions")
    op.drop_table("ai_chat_sessions")
