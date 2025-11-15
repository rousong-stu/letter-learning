"""add consecutive known hits to user word book words

Revision ID: 8e3c31a8c5e9
Revises: 7c6d4a5c4635
Create Date: 2025-11-16 10:00:00.000000

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "8e3c31a8c5e9"
down_revision = "7c6d4a5c4635"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "user_word_book_words",
        sa.Column(
            "consecutive_known_hits",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="连续“我认识”次数",
        ),
    )


def downgrade() -> None:
    op.drop_column("user_word_book_words", "consecutive_known_hits")
