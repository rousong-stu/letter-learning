from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import BigInteger, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func, text

from app.models.base import Base


class User(Base):
    """平台用户实体。"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="主键"
    )
    username: Mapped[str] = mapped_column(
        String(128), unique=True, nullable=False, comment="唯一登录名"
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(255), unique=True, nullable=True, comment="邮箱"
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(32), unique=True, nullable=True, comment="手机号"
    )
    password_hash: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="密码哈希"
    )
    display_name: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="展示名称"
    )
    avatar_url: Mapped[Optional[str]] = mapped_column(
        String(512), nullable=True, comment="头像地址"
    )
    status: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default=text("1"),
        comment="1=启用，0=禁用",
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最近登录时间"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="创建时间",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )

    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary="user_roles",
        back_populates="users",
        lazy="selectin",
    )
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    verification_codes: Mapped[List["VerificationCode"]] = relationship(
        "VerificationCode",
        back_populates="user",
        lazy="selectin",
    )
    password_reset_requests: Mapped[List["PasswordResetRequest"]] = relationship(
        "PasswordResetRequest",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="user",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<User username={self.username!r}>"

