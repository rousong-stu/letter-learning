from __future__ import annotations

from datetime import datetime, date
from typing import Any, Iterable, Optional, Sequence

from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import (
    User,
    UserLoginLog,
    UserProfile,
    UserPasswordHistory,
)


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


async def list_users(
    session: AsyncSession,
    *,
    username: str | None = None,
    offset: int = 0,
    limit: int = 10,
) -> Sequence[User]:
    stmt = (
        select(User)
        .order_by(User.id.desc())
        .offset(offset)
        .limit(limit)
    )
    if username:
        stmt = stmt.where(User.username.like(f"%{username}%"))
    result = await session.execute(stmt)
    return result.scalars().all()


async def count_users(session: AsyncSession, *, username: str | None = None) -> int:
    stmt = select(func.count(User.id))
    if username:
        stmt = stmt.where(User.username.like(f"%{username}%"))
    result = await session.execute(stmt)
    return result.scalar_one()


async def update_user(
    session: AsyncSession,
    user: User,
    *,
    username: str | None = None,
    email: str | None = None,
    password_hash: str | None = None,
) -> User:
    if username is not None:
        user.username = username
    if email is not None:
        user.email = email
    if password_hash:
        user.password_hash = password_hash
    await session.flush()
    return user


async def delete_users(session: AsyncSession, user_ids: Iterable[int]) -> int:
    stmt = delete(User).where(User.id.in_(list(user_ids)))
    result = await session.execute(stmt)
    await session.flush()
    return result.rowcount or 0


async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
    stmt = (
        select(User)
        .options(selectinload(User.profile))
        .where(User.id == user_id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def ensure_email_available(session: AsyncSession, user_id: int, email: str) -> None:
    existing = await get_user_by_email(session, email)
    if existing and existing.id != user_id:
        raise ValueError("邮箱已被占用")


async def ensure_phone_available(session: AsyncSession, user_id: int, phone: str) -> None:
    existing = await get_user_by_phone(session, phone)
    if existing and existing.id != user_id:
        raise ValueError("手机号已被占用")


async def update_user_fields(
    session: AsyncSession,
    user: User,
    fields: dict[str, Any],
) -> User:
    for key, value in fields.items():
        setattr(user, key, value)
    await session.flush()
    return user


async def upsert_user_profile(
    session: AsyncSession, user_id: int, data: dict
) -> UserProfile:
    stmt = select(UserProfile).where(UserProfile.user_id == user_id)
    result = await session.execute(stmt)
    profile = result.scalar_one_or_none()
    if profile is None:
        profile = UserProfile(user_id=user_id)
        session.add(profile)
    for field, value in data.items():
        setattr(profile, field, value)
    await session.flush()
    return profile


async def add_password_history(
    session: AsyncSession, user_id: int, password_hash: str, changed_by: Optional[int]
) -> None:
    history = UserPasswordHistory(
        user_id=user_id,
        password_hash=password_hash,
        changed_by=changed_by,
    )
    session.add(history)
    await session.flush()


async def create_login_log(
    session: AsyncSession,
    *,
    user_id: int,
    login_at: datetime,
    ip_address: Optional[str],
    user_agent: Optional[str],
    device_name: Optional[str],
    location: Optional[str],
    successful: bool,
    token_id: Optional[str],
) -> UserLoginLog:
    log = UserLoginLog(
        user_id=user_id,
        login_at=login_at,
        ip_address=ip_address,
        user_agent=user_agent,
        device_name=device_name,
        location=location,
        successful=1 if successful else 0,
        token_id=token_id,
    )
    session.add(log)
    await session.flush()
    return log


async def mark_logout_at(session: AsyncSession, token_id: str, logout_at):
    stmt = (
        update(UserLoginLog)
        .where(UserLoginLog.token_id == token_id, UserLoginLog.logout_at.is_(None))
        .values(logout_at=logout_at)
    )
    await session.execute(stmt)
    await session.flush()


async def list_login_logs(
    session: AsyncSession, user_id: int, limit: int = 10
) -> Sequence[UserLoginLog]:
    stmt = (
        select(UserLoginLog)
        .where(UserLoginLog.user_id == user_id)
        .order_by(UserLoginLog.login_at.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    return result.scalars().all()
