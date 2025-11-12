"""role permissions mapping

Revision ID: bf170bbacdad
Revises: 7a8c11cbc48c
Create Date: 2025-11-11 21:39:28.223184

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlalchemy.sql import text
from sqlalchemy.orm import Session


def bigint():
    base = sa.BigInteger()
    base = base.with_variant(sa.Integer(), "sqlite")
    base = base.with_variant(mysql.BIGINT(unsigned=True), "mysql")
    return base


# revision identifiers, used by Alembic.
revision = 'bf170bbacdad'
down_revision = '1f5a408f0615'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'role_permissions',
        sa.Column('id', bigint(), primary_key=True, autoincrement=True),
        sa.Column('role_id', bigint(), nullable=False),
        sa.Column(
            'permission_type',
            sa.String(length=32),
            nullable=False,
            comment='menu / action',
        ),
        sa.Column(
            'permission_value',
            sa.String(length=255),
            nullable=False,
            comment='路由路径或权限编码',
        ),
        sa.Column(
            'created_at',
            sa.DateTime(),
            nullable=False,
            server_default=sa.text('CURRENT_TIMESTAMP'),
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(),
            nullable=False,
            server_default=sa.text('CURRENT_TIMESTAMP'),
            onupdate=sa.text('CURRENT_TIMESTAMP'),
        ),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
    )
    op.create_index(
        'idx_role_permissions_role_type',
        'role_permissions',
        ['role_id', 'permission_type'],
    )

    bind = op.get_bind()
    session = Session(bind=bind)
    defaults = {
        'super_admin': ['read:system', 'write:system', 'delete:system'],
        'admin': ['read:system', 'write:system'],
        'user': ['read:system'],
    }
    try:
        for slug, perms in defaults.items():
            role = session.execute(
                text("SELECT id FROM roles WHERE slug = :slug"),
                {'slug': slug},
            ).first()
            if not role:
                continue
            role_id = role.id if hasattr(role, 'id') else role[0]
            for perm in perms:
                session.execute(
                    text(
                        """
                        INSERT INTO role_permissions (role_id, permission_type, permission_value)
                        VALUES (:role_id, :ptype, :pvalue)
                        """
                    ),
                    {
                        'role_id': role_id,
                        'ptype': 'action',
                        'pvalue': perm,
                    },
                )
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def downgrade() -> None:
    op.drop_index('idx_role_permissions_role_type', table_name='role_permissions')
    op.drop_table('role_permissions')
