from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models import RefreshToken, Role, User
from app.repositories import token as token_repo
from app.repositories import user as user_repo

settings = get_settings()


async def authenticate_user(
    session: AsyncSession, *, username: str, password: str
) -> Optional[User]:
    user = await user_repo.get_user_by_username(session, username)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    if user.status != 1:
        raise ValueError("账户已被禁用")
    return user


async def register_user(
    session: AsyncSession,
    *,
    username: str,
    password: str,
    email: str | None = None,
    assign_roles: Iterable[str] | None = None,
) -> User:
    if await user_repo.get_user_by_username(session, username):
        raise ValueError("用户名已存在")
    if email and await user_repo.get_user_by_email(session, email):
        raise ValueError("邮箱已被占用")

    password_hash = get_password_hash(password)

    user = await user_repo.create_user(
        session,
        username=username,
        password_hash=password_hash,
        email=email,
        display_name=username,
    )
    user.password_updated_at = datetime.utcnow()
    await user_repo.add_password_history(
        session,
        user_id=user.id,
        password_hash=password_hash,
        changed_by=user.id,
    )

    if assign_roles:
        await user_repo.replace_user_roles(session, user, assign_roles)
    return user


async def issue_token_pair(
    session: AsyncSession,
    *,
    user: User,
    roles: list[str] | None = None,
    user_agent: str | None = None,
    ip_address: str | None = None,
) -> tuple[str, RefreshToken]:
    additional_claims = {
        "username": user.username,
        "roles": roles or [],
    }
    token, token_id, expire_at = create_access_token(
        user.id, additional_claims=additional_claims
    )
    refresh_expires = datetime.utcnow() + timedelta(
        days=settings.refresh_token_expire_days
    )
    refresh_token_record = await token_repo.create_refresh_token(
        session,
        user_id=user.id,
        token_id=token_id,
        expires_at=refresh_expires,
        user_agent=user_agent,
        ip_address=ip_address,
    )
    user.last_login_at = datetime.utcnow()
    return token, refresh_token_record


async def revoke_token(session: AsyncSession, token_id: str) -> None:
    await token_repo.revoke_refresh_token(session, token_id)


def format_role_names(roles: Iterable[Role]) -> list[str]:
    """将角色 slug 转换为前端 guard 名称。"""
    mapping = {
        "admin": "Admin",
        "teacher": "Teacher",
        "student": "Student",
    }
    result = []
    for role in roles:
        result.append(mapping.get(role.slug, role.slug.title()))
    return result
