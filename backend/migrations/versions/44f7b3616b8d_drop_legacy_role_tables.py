"""drop legacy role & permission tables

Revision ID: 44f7b3616b8d
Revises: 1f5a408f0615
Create Date: 2025-11-14 09:10:00.000000

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op


def _bigint():
    base = sa.BigInteger()
    base = base.with_variant(sa.Integer(), "sqlite")
    return base


# revision identifiers, used by Alembic.
revision = "44f7b3616b8d"
down_revision = "1f5a408f0615"
branch_labels = None
depends_on = None


def upgrade() -> None:
    tables = [
        "role_permissions",
        "user_roles",
        "menus",
        "roles",
        "verification_codes",
        "password_reset_requests",
        "audit_logs",
    ]
    for table in tables:
        op.execute(f"DROP TABLE IF EXISTS {table}")


def downgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", _bigint(), primary_key=True, autoincrement=True),
        sa.Column("slug", sa.String(length=64), nullable=False, unique=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.String(length=512)),
        sa.Column(
            "is_system",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("1"),
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
            onupdate=sa.text("CURRENT_TIMESTAMP"),
        ),
    )

    op.create_table(
        "user_roles",
        sa.Column("id", _bigint(), primary_key=True, autoincrement=True),
        sa.Column("user_id", _bigint(), nullable=False),
        sa.Column("role_id", _bigint(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE", onupdate="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["role_id"], ["roles.id"], ondelete="CASCADE", onupdate="CASCADE"
        ),
        sa.UniqueConstraint("user_id", "role_id", name="uq_user_roles_user_role"),
    )

    op.create_table(
        "role_permissions",
        sa.Column("id", _bigint(), primary_key=True, autoincrement=True),
        sa.Column("role_id", _bigint(), nullable=False),
        sa.Column("permission_type", sa.String(length=32), nullable=False),
        sa.Column("permission_value", sa.String(length=255), nullable=False),
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
            onupdate=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["role_id"], ["roles.id"], ondelete="CASCADE", onupdate="CASCADE"
        ),
    )

    op.create_table(
        "menus",
        sa.Column("id", _bigint(), primary_key=True, autoincrement=True),
        sa.Column("parent_id", _bigint(), nullable=True),
        sa.Column("title", sa.String(length=128), nullable=False),
        sa.Column("path", sa.String(length=255), nullable=False, unique=True),
        sa.Column("component", sa.String(length=255)),
        sa.Column("icon", sa.String(length=64)),
        sa.Column(
            "type",
            sa.String(length=16),
            nullable=False,
            server_default=sa.text("'menu'"),
        ),
        sa.Column(
            "order_no",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "is_external",
            sa.SmallInteger(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "is_cache",
            sa.SmallInteger(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "is_hidden",
            sa.SmallInteger(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column("redirect", sa.String(length=255)),
        sa.Column(
            "status",
            sa.SmallInteger(),
            nullable=False,
            server_default=sa.text("1"),
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
            onupdate=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"], ["menus.id"], ondelete="CASCADE", onupdate="CASCADE"
        ),
    )

    op.create_table(
        "verification_codes",
        sa.Column("id", _bigint(), primary_key=True, autoincrement=True),
        sa.Column("user_id", _bigint(), nullable=True),
        sa.Column("channel", sa.String(length=32), nullable=False),
        sa.Column("recipient", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=16), nullable=False),
        sa.Column("purpose", sa.String(length=32), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("consumed_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="SET NULL", onupdate="CASCADE"
        ),
    )

    op.create_table(
        "password_reset_requests",
        sa.Column("id", _bigint(), primary_key=True, autoincrement=True),
        sa.Column("user_id", _bigint(), nullable=False),
        sa.Column("reset_token", sa.String(length=255), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("used_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE", onupdate="CASCADE"
        ),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", _bigint(), primary_key=True, autoincrement=True),
        sa.Column("user_id", _bigint(), nullable=True),
        sa.Column("action", sa.String(length=128), nullable=False),
        sa.Column("description", sa.String(length=512)),
        sa.Column("ip_address", sa.String(length=64)),
        sa.Column("user_agent", sa.String(length=512)),
        sa.Column("metadata", sa.JSON()),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="SET NULL", onupdate="CASCADE"
        ),
    )
