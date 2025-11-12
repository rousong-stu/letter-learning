"""fix_home_menu_component

Revision ID: cad3a9b7ceeb
Revises: 770fed70558c
Create Date: 2025-11-12 22:39:16.581837

"""
from __future__ import annotations

from alembic import op


# revision identifiers, used by Alembic.
revision = 'cad3a9b7ceeb'
down_revision = '770fed70558c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE menus
        SET component='@/views/index/index'
        WHERE path='/home' AND (component IS NULL OR component='@/views/dashboard/workplace')
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE menus
        SET component='@/views/dashboard/workplace'
        WHERE path='/home' AND component='@/views/index/index'
        """
    )
