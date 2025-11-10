"""initial schema

Revision ID: 1bbf83c969d8
Revises: 
Create Date: 2025-11-03 22:55:17.149511

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.orm import Session

from app.models import Base
from app.models.auth import Role, UserRole
from app.models.user import User


# revision identifiers, used by Alembic.
revision = '1bbf83c969d8'
down_revision = None
branch_labels = None
depends_on = None

ADMIN_DEFAULT_PASSWORD_HASH = "$2b$12$/Znhr8AkcELjhN93NxxwkuBfLlVrcnUjT/X.Cj2uMxpCJPDKiB17u"


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind)

    session = Session(bind=bind)
    try:
        role_defs = [
            {
                "slug": "admin",
                "name": "管理员",
                "description": "平台超级管理员",
                "is_system": 1,
            },
            {
                "slug": "teacher",
                "name": "教师",
                "description": "教师权限",
                "is_system": 1,
            },
            {
                "slug": "student",
                "name": "学生",
                "description": "学生权限",
                "is_system": 1,
            },
        ]

        role_map: dict[str, Role] = {}
        for data in role_defs:
            role = session.query(Role).filter_by(slug=data["slug"]).one_or_none()
            if role is None:
                role = Role(**data)
                session.add(role)
                session.flush()
            role_map[data["slug"]] = role

        admin = session.query(User).filter_by(username="admin").one_or_none()
        if admin is None:
            admin = User(
                username="admin",
                email="admin@example.com",
                password_hash=ADMIN_DEFAULT_PASSWORD_HASH,
                display_name="系统管理员",
                status=1,
            )
            session.add(admin)
            session.flush()
        else:
            admin.password_hash = ADMIN_DEFAULT_PASSWORD_HASH
            admin.status = 1
            if not admin.display_name:
                admin.display_name = "系统管理员"
            session.flush()

        admin_role = role_map.get("admin")
        if admin_role:
            has_relation = (
                session.query(UserRole)
                .filter_by(user_id=admin.id, role_id=admin_role.id)
                .first()
            )
            if not has_relation:
                session.add(UserRole(user_id=admin.id, role_id=admin_role.id))

        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind)
