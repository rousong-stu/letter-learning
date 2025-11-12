"""menu management

Revision ID: 2d5f7a1e1dcd
Revises: bf170bbacdad
Create Date: 2025-11-12 15:19:53.354285

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import Session
from sqlalchemy.sql import text


def bigint():
    base = sa.BigInteger()
    base = base.with_variant(sa.Integer(), "sqlite")
    base = base.with_variant(mysql.BIGINT(unsigned=True), "mysql")
    return base


# revision identifiers, used by Alembic.
revision = '2d5f7a1e1dcd'
down_revision = 'bf170bbacdad'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "menus",
        sa.Column("id", bigint(), primary_key=True, autoincrement=True),
        sa.Column("parent_id", bigint(), nullable=True),
        sa.Column("title", sa.String(length=128), nullable=False),
        sa.Column("path", sa.String(length=255), nullable=False),
        sa.Column("component", sa.String(length=255), nullable=True),
        sa.Column("icon", sa.String(length=64), nullable=True),
        sa.Column("type", sa.String(length=16), nullable=False, server_default=sa.text("'menu'")),
        sa.Column("order_no", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("is_external", sa.SmallInteger(), nullable=False, server_default=sa.text("0")),
        sa.Column("is_cache", sa.SmallInteger(), nullable=False, server_default=sa.text("0")),
        sa.Column("is_hidden", sa.SmallInteger(), nullable=False, server_default=sa.text("0")),
        sa.Column("redirect", sa.String(length=255), nullable=True),
        sa.Column("status", sa.SmallInteger(), nullable=False, server_default=sa.text("1")),
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
        sa.ForeignKeyConstraint(["parent_id"], ["menus.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_menus_parent", "menus", ["parent_id"])
    op.create_index("uq_menus_path", "menus", ["path"], unique=True)

    # seed basic menus
    bind = op.get_bind()
    session = Session(bind=bind)
    menu_defs = [
        (None, "首页", "/home", "@/views/dashboard/workplace", "home-filled", "menu", 1),
        (None, "配置", "/setting", "Layout", "setting", "catalog", 99),
        ("setting", "用户管理", "/setting/userManagement", "@/views/setting/userManagement/index", "user", "menu", 1),
        ("setting", "角色管理", "/setting/roleManagement", "@/views/setting/roleManagement/index", "tickets", "menu", 2),
        ("setting", "菜单管理", "/setting/menuManagement", "@/views/setting/menuManagement/index", "menu", "menu", 3),
        ("setting", "字典管理", "/setting/dictionaryManagement", "@/views/setting/dictionaryManagement/index", "collection", "menu", 4),
        ("setting", "任务管理", "/setting/taskManagement", "@/views/setting/taskManagement/index", "list", "menu", 5),
        ("setting", "系统日志", "/setting/systemLog", "@/views/setting/systemLog/index", "document", "menu", 6),
        ("setting", "个人中心", "/setting/personalCenter", "@/views/setting/personalCenter/index", "avatar", "menu", 7),
    ]
    slug_to_id = {}
    try:
        for parent_slug, title, path, component, icon, mtype, order_no in menu_defs:
            parent_id = slug_to_id.get(parent_slug)
            result = session.execute(
                text(
                    """
                    INSERT INTO menus (parent_id, title, path, component, icon, type, order_no)
                    VALUES (:parent_id, :title, :path, :component, :icon, :type, :order_no)
                    """
                ),
                {
                    "parent_id": parent_id,
                    "title": title,
                    "path": path,
                    "component": component or None,
                    "icon": icon,
                    "type": mtype,
                    "order_no": order_no,
                },
            )
            inserted_id = result.lastrowid
            slug_to_id[path.split("/")[-1] if path else title] = inserted_id

        # grant super admin role all menus
        admin_role = session.execute(text("SELECT id FROM roles WHERE slug='super_admin'"))
        admin_role = admin_role.first()
        if admin_role:
            menu_ids = session.execute(text("SELECT id FROM menus")).all()
            for (menu_id,) in menu_ids:
                session.execute(
                    text(
                        """
                        INSERT INTO role_permissions (role_id, permission_type, permission_value)
                        VALUES (:role_id, 'menu', :menu_id)
                        """
                    ),
                    {"role_id": admin_role[0], "menu_id": str(menu_id)},
                )
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def downgrade() -> None:
    op.drop_index("uq_menus_path", table_name="menus")
    op.drop_index("idx_menus_parent", table_name="menus")
    op.drop_table("menus")
