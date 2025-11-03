from __future__ import annotations

from typing import Iterable, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Role, User, UserRole


async def get_user_by_username(session: AsyncSession, username: str) -> Optional[User]:
    stmt = select(User).where(User.username == username)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_phone(session: AsyncSession, phone: str) -> Optional[User]:
    stmt = select(User).where(User.phone == phone)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    stmt = select(User).where(User.email == email)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(
    session: AsyncSession,
    *,
    username: str,
    password_hash: str,
    phone: str | None = None,
    email: str | None = None,
    display_name: str | None = None,
) -> User:
    user = User(
        username=username,
        password_hash=password_hash,
        phone=phone,
        email=email,
        display_name=display_name or username,
    )
    session.add(user)
    try:
        await session.flush()
    except IntegrityError as exc:
        await session.rollback()
        raise ValueError("用户名或联系信息已存在") from exc
    return user


async def assign_roles(session: AsyncSession, user: User, role_slugs: Iterable[str]) -> None:
    if not role_slugs:
        return
    stmt = select(Role).where(Role.slug.in_(list(role_slugs)))
    result = await session.execute(stmt)
    roles = result.scalars().all()
    if not roles:
        raise ValueError("角色不存在")
    for role in roles:
        session.add(UserRole(user_id=user.id, role_id=role.id))
    await session.flush()

