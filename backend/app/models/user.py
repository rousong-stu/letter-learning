from __future__ import annotations

from datetime import datetime, date
from typing import List, Optional

from sqlalchemy import Date, DateTime, ForeignKey, Integer, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func, text

from app.models.base import Base
from app.models.types import bigint


class User(Base):
    """平台用户实体。"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        bigint(), primary_key=True, autoincrement=True, comment="主键"
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
    gender: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=0,
        server_default=text("0"),
        comment="0=未知,1=男,2=女",
    )
    birthday: Mapped[Optional[date]] = mapped_column(Date, nullable=True, comment="生日")
    locale: Mapped[Optional[str]] = mapped_column(
        String(16), nullable=True, comment="语言偏好"
    )
    timezone: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="时区"
    )
    signature: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="个性签名"
    )
    password_updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最后一次密码修改时间"
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

    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="noload",
    )
    profile: Mapped[Optional["UserProfile"]] = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="noload",
    )
    password_histories: Mapped[List["UserPasswordHistory"]] = relationship(
        "UserPasswordHistory",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="noload",
        foreign_keys="UserPasswordHistory.user_id",
    )
    login_logs: Mapped[List["UserLoginLog"]] = relationship(
        "UserLoginLog",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="noload",
    )
    word_stories: Mapped[List["WordStory"]] = relationship(
        "WordStory",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="noload",
    )

    def __repr__(self) -> str:
        return f"<User username={self.username!r}>"


class UserProfile(Base):
    """用户补充资料。"""

    __tablename__ = "user_profiles"

    user_id: Mapped[int] = mapped_column(
        bigint(),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        comment="用户主键",
    )
    real_name: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True, comment="真实姓名"
    )
    id_number: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="证件号/学号"
    )
    address: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="联系地址"
    )
    wechat: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="微信"
    )
    qq: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, comment="QQ")
    linkedin: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True, comment="LinkedIn"
    )
    website: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="个人主页"
    )
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="简介")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间",
    )

    user: Mapped["User"] = relationship("User", back_populates="profile", lazy="joined")


class UserPasswordHistory(Base):
    """用户密码历史记录。"""

    __tablename__ = "user_password_history"

    id: Mapped[int] = mapped_column(
        bigint(), primary_key=True, autoincrement=True, comment="主键"
    )
    user_id: Mapped[int] = mapped_column(
        bigint(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="用户主键",
    )
    password_hash: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="密码哈希"
    )
    changed_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, comment="修改时间"
    )
    changed_by: Mapped[Optional[int]] = mapped_column(
        bigint(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="操作者",
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="password_histories",
        lazy="joined",
        foreign_keys="UserPasswordHistory.user_id",
    )
    changed_by_user: Mapped[Optional["User"]] = relationship(
        "User",
        lazy="joined",
        foreign_keys="UserPasswordHistory.changed_by",
    )


class UserLoginLog(Base):
    """用户登录日志。"""

    __tablename__ = "user_login_logs"

    id: Mapped[int] = mapped_column(
        bigint(), primary_key=True, autoincrement=True, comment="主键"
    )
    user_id: Mapped[int] = mapped_column(
        bigint(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="用户主键",
    )
    login_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, comment="登录时间"
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="IP 地址"
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        String(512), nullable=True, comment="User-Agent"
    )
    device_name: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True, comment="设备"
    )
    location: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True, comment="地理位置"
    )
    successful: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=1,
        server_default=text("1"),
        comment="是否成功",
    )
    token_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="刷新令牌ID"
    )
    logout_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="登出时间"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, comment="记录时间"
    )

    user: Mapped["User"] = relationship(
        "User", back_populates="login_logs", lazy="joined"
    )
