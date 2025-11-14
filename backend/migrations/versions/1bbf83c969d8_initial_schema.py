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

        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind)
