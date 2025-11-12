"""update default roles

Revision ID: 770fed70558c
Revises: 2d5f7a1e1dcd
Create Date: 2025-11-12 16:34:27.056731

"""
from __future__ import annotations

from alembic import op
from sqlalchemy.orm import Session
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision = '770fed70558c'
down_revision = '2d5f7a1e1dcd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        session.execute(
            text(
                "UPDATE roles SET slug='super_admin', name='超级管理员', description='系统超级管理员' WHERE slug='admin'"
            )
        )
        session.execute(
            text(
                "UPDATE roles SET slug='admin', name='管理员', description='系统管理员' WHERE slug='teacher'"
            )
        )
        session.execute(
            text(
                "UPDATE roles SET slug='user', name='用户', description='普通用户' WHERE slug='student'"
            )
        )
        admin_user = session.execute(
            text("SELECT id FROM users WHERE username='admin'")
        ).first()
        super_role = session.execute(
            text("SELECT id FROM roles WHERE slug='super_admin'")
        ).first()
        admin_role = session.execute(
            text("SELECT id FROM roles WHERE slug='admin'")
        ).first()
        if admin_user and super_role:
            session.execute(
                text("DELETE FROM user_roles WHERE user_id=:uid"),
                {"uid": admin_user[0]},
            )
            session.execute(
                text(
                    "INSERT INTO user_roles (user_id, role_id) VALUES (:uid, :rid)"
                ),
                {"uid": admin_user[0], "rid": super_role[0]},
            )
        if admin_role:
            ceshi_users = session.execute(
                text("SELECT id FROM users WHERE username LIKE 'ceshi%'")
            ).all()
            for (uid,) in ceshi_users:
                session.execute(
                    text("DELETE FROM user_roles WHERE user_id=:uid"),
                    {"uid": uid},
                )
                session.execute(
                    text(
                        "INSERT INTO user_roles (user_id, role_id) VALUES (:uid, :rid)"
                    ),
                    {"uid": uid, "rid": admin_role[0]},
                )
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def downgrade() -> None:
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        session.execute(
            text(
                "UPDATE roles SET slug='admin', name='管理员', description='平台超级管理员' WHERE slug='super_admin'"
            )
        )
        session.execute(
            text(
                "UPDATE roles SET slug='teacher', name='教师', description='教师权限' WHERE slug='admin'"
            )
        )
        session.execute(
            text(
                "UPDATE roles SET slug='student', name='学生', description='学生权限' WHERE slug='user'"
            )
        )
        admin_user = session.execute(
            text("SELECT id FROM users WHERE username='admin'")
        ).first()
        admin_role = session.execute(
            text("SELECT id FROM roles WHERE slug='admin'")
        ).first()
        if admin_user and admin_role:
            session.execute(
                text("DELETE FROM user_roles WHERE user_id=:uid"),
                {"uid": admin_user[0]},
            )
            session.execute(
                text(
                    "INSERT INTO user_roles (user_id, role_id) VALUES (:uid, :rid)"
                ),
                {"uid": admin_user[0], "rid": admin_role[0]},
            )
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
