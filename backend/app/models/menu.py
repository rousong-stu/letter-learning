from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base
from app.models.types import bigint


class Menu(Base):
    """系统菜单/路由节点。"""

    __tablename__ = "menus"

    id: Mapped[int] = mapped_column(
        bigint(), primary_key=True, autoincrement=True, comment="主键"
    )
    parent_id: Mapped[Optional[int]] = mapped_column(
        bigint(),
        ForeignKey("menus.id", ondelete="CASCADE"),
        nullable=True,
        comment="父级 ID",
    )
    title: Mapped[str] = mapped_column(String(128), nullable=False, comment="标题")
    path: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, comment="路由路径")
    component: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="组件路径")
    icon: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, comment="图标")
    type: Mapped[str] = mapped_column(
        String(16), nullable=False, default="menu", server_default="menu", comment="目录/菜单/按钮"
    )
    order_no: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0", comment="排序"
    )
    is_external: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default="0", comment="是否外链"
    )
    is_cache: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default="0", comment="是否缓存"
    )
    is_hidden: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default="0", comment="是否隐藏"
    )
    redirect: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="重定向路径")
    status: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=1, server_default="1", comment="1=启用"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )

    parent: Mapped[Optional["Menu"]] = relationship(
        "Menu", remote_side=[id], back_populates="children", lazy="selectin"
    )
    children: Mapped[List["Menu"]] = relationship(
        "Menu", back_populates="parent", cascade="all, delete-orphan", lazy="selectin"
    )


class RolePermission(Base):
    """角色权限映射表。"""

    __tablename__ = "role_permissions"

    id: Mapped[int] = mapped_column(
        bigint(), primary_key=True, autoincrement=True, comment="主键"
    )
    role_id: Mapped[int] = mapped_column(
        bigint(),
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        comment="角色主键",
    )
    permission_type: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="menu/action"
    )
    permission_value: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="权限编码或菜单ID"
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

    role: Mapped["Role"] = relationship(
        "Role",
        back_populates="permissions",
        lazy="raise_on_sql",
    )
