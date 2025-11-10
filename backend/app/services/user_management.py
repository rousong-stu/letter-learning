from __future__ import annotations

from typing import Iterable

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models import User
from app.repositories import user as user_repo


async def paginate_users(
    session: AsyncSession,
    *,
    username: str | None,
    page_no: int,
    page_size: int,
) -> tuple[list[User], int]:
    offset = (page_no - 1) * page_size
    users = await user_repo.list_users(
        session,
        username=username,
        offset=offset,
        limit=page_size,
    )
    total = await user_repo.count_users(session, username=username)
    return list(users), total


async def create_user_with_roles(
    session: AsyncSession,
    *,
    username: str,
    password: str,
    email: str | None,
    roles: Iterable[str],
) -> User:
    if await user_repo.get_user_by_username(session, username):
        raise ValueError("用户名已存在")

    password_hash = get_password_hash(password)
    user = await user_repo.create_user(
        session,
        username=username,
        password_hash=password_hash,
        email=email,
    )
    await user_repo.replace_user_roles(session, user, roles)
    return user


async def update_user_with_roles(
    session: AsyncSession,
    *,
    user_id: int,
    username: str,
    email: str | None,
    password: str | None,
    roles: Iterable[str],
) -> User:
    user = await session.get(User, user_id)
    if not user:
        raise ValueError("用户不存在")

    existing = await user_repo.get_user_by_username(session, username)
    if existing and existing.id != user_id:
        raise ValueError("用户名已存在")

    password_hash = get_password_hash(password) if password else None

    await user_repo.update_user(
        session,
        user,
        username=username,
        email=email,
        password_hash=password_hash,
    )
    await user_repo.replace_user_roles(session, user, roles)
    return user


async def delete_users(session: AsyncSession, user_ids: Iterable[int]) -> int:
    return await user_repo.delete_users(session, user_ids)
