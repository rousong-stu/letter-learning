from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base
from app.models.types import bigint


class RefreshToken(Base):
    """刷新令牌记录，用于 JWT 轮换。"""

    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(
        bigint(), primary_key=True, autoincrement=True, comment="主键"
    )
    user_id: Mapped[int] = mapped_column(
        bigint(),
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="用户主键",
    )
    token: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, comment="刷新令牌"
    )
    issued_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="发放时间",
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="过期时间"
    )
    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="撤销时间"
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        String(512), nullable=True, comment="客户端 UA"
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="客户端 IP"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="创建时间",
    )

    user: Mapped["User"] = relationship(
        "User", back_populates="refresh_tokens", lazy="joined"
    )
