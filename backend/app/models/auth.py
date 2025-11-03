from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import (
    JSON,
    BigInteger,
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func, text

from app.models.base import Base


class Role(Base):
    """角色实体，定义平台权限范围。"""

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="主键"
    )
    slug: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, comment="角色唯一编码"
    )
    name: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="角色名称"
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(512), nullable=True, comment="角色描述"
    )
    is_system: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default=text("1"),
        comment="1=系统内置角色，0=自定义角色",
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

    users: Mapped[List["User"]] = relationship(
        "User",
        secondary="user_roles",
        back_populates="roles",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Role slug={self.slug!r}>"


class UserRole(Base):
    """用户与角色的关系表。"""

    __tablename__ = "user_roles"
    __table_args__ = (
        UniqueConstraint("user_id", "role_id", name="uq_user_roles_user_role"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="主键"
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="用户主键",
    )
    role_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("roles.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="角色主键",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="创建时间",
    )


class RefreshToken(Base):
    """刷新令牌记录，用于 JWT 轮换。"""

    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="主键"
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
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


class VerificationChannel(Enum):
    EMAIL = "email"
    SMS = "sms"


class VerificationPurpose(Enum):
    REGISTER = "register"
    LOGIN = "login"
    RESET_PASSWORD = "reset_password"
    MFA = "mfa"


class VerificationCode(Base):
    """验证码记录，用于各类验证流程。"""

    __tablename__ = "verification_codes"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="主键"
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        comment="用户主键，注册前可为空",
    )
    channel: Mapped[VerificationChannel] = mapped_column(
        SqlEnum(
            VerificationChannel,
            name="verification_channel",
            native_enum=True,
            create_constraint=False,
        ),
        nullable=False,
        comment="发送渠道",
    )
    recipient: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="收件人（邮箱或手机号）"
    )
    code: Mapped[str] = mapped_column(
        String(16), nullable=False, comment="验证码"
    )
    purpose: Mapped[VerificationPurpose] = mapped_column(
        SqlEnum(
            VerificationPurpose,
            name="verification_purpose",
            native_enum=True,
            create_constraint=False,
        ),
        nullable=False,
        comment="使用场景",
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="过期时间"
    )
    consumed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="使用时间"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="创建时间",
    )

    user: Mapped[Optional["User"]] = relationship(
        "User", back_populates="verification_codes", lazy="joined"
    )


class PasswordResetRequest(Base):
    """密码重置请求记录。"""

    __tablename__ = "password_reset_requests"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="主键"
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="用户主键",
    )
    reset_token: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, comment="重置令牌"
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="过期时间"
    )
    used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="使用时间"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="创建时间",
    )

    user: Mapped["User"] = relationship(
        "User", back_populates="password_reset_requests", lazy="joined"
    )


class AuditLog(Base):
    """安全审计日志。"""

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="主键"
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        comment="关联用户主键",
    )
    action: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="动作标识"
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(512), nullable=True, comment="描述信息"
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="来源 IP"
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        String(512), nullable=True, comment="客户端 UA"
    )
    metadata: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="额外元数据"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="记录时间",
    )

    user: Mapped[Optional["User"]] = relationship(
        "User", back_populates="audit_logs", lazy="joined"
    )

