"""add image fields to word stories

Revision ID: b6b25e41ce09
Revises: 9c954c6d8f92
Create Date: 2025-11-15 17:20:00.000000

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "b6b25e41ce09"
down_revision = "9c954c6d8f92"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "word_stories",
        sa.Column(
            "image_url",
            sa.String(length=1024),
            nullable=True,
            comment="生成的插图 URL",
        ),
    )
    op.add_column(
        "word_stories",
        sa.Column(
            "image_caption",
            sa.Text(),
            nullable=True,
            comment="插图描述",
        ),
    )


def downgrade() -> None:
    op.drop_column("word_stories", "image_caption")
    op.drop_column("word_stories", "image_url")
