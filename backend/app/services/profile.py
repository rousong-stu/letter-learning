from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import get_password_hash, verify_password
from app.models import User
from app.repositories import user as user_repo

settings = get_settings()


USER_FIELD_MAPPING = {
    "displayName": "display_name",
    "email": "email",
    "phone": "phone",
    "gender": "gender",
    "birthday": "birthday",
    "locale": "locale",
    "timezone": "timezone",
    "signature": "signature",
}

PROFILE_FIELD_MAPPING = {
    "realName": "real_name",
    "idNumber": "id_number",
    "address": "address",
    "wechat": "wechat",
    "qq": "qq",
    "linkedin": "linkedin",
    "website": "website",
    "bio": "bio",
}


async def get_profile(
    session: AsyncSession, user_id: int, *, log_limit: int = 10
):
    user = await user_repo.get_user_by_id(session, user_id)
    if not user:
        raise ValueError("用户不存在")
    profile = user.profile or await user_repo.upsert_user_profile(session, user.id, {})
    logs = await user_repo.list_login_logs(session, user_id, limit=log_limit)
    return user, profile, logs


async def update_profile(
    session: AsyncSession,
    user: User,
    payload: dict[str, Optional[object]],
) -> User:
    user_fields: dict[str, Optional[object]] = {}
    profile_fields: dict[str, Optional[object]] = {}

    for client_field, db_field in USER_FIELD_MAPPING.items():
        if client_field in payload:
            user_fields[db_field] = payload[client_field]

    for client_field, db_field in PROFILE_FIELD_MAPPING.items():
        if client_field in payload:
            profile_fields[db_field] = payload[client_field]

    if "email" in user_fields:
        email_value = user_fields["email"]
        if email_value:
            await user_repo.ensure_email_available(
                session, user.id, email_value  # type: ignore[arg-type]
            )
        else:
            user_fields["email"] = None
    if "phone" in user_fields:
        phone_value = user_fields["phone"]
        if phone_value:
            await user_repo.ensure_phone_available(
                session, user.id, phone_value  # type: ignore[arg-type]
            )
        else:
            user_fields["phone"] = None

    if user_fields:
        await user_repo.update_user_fields(session, user, user_fields)
    if profile_fields:
        await user_repo.upsert_user_profile(session, user.id, profile_fields)

    await session.flush()
    return await user_repo.get_user_by_id(session, user.id)  # type: ignore[return-value]


async def change_password(
    session: AsyncSession,
    user: User,
    *,
    old_password: str,
    new_password: str,
    changed_by: Optional[int] = None,
) -> None:
    if not verify_password(old_password, user.password_hash):
        raise ValueError("原密码不正确")
    if verify_password(new_password, user.password_hash):
        raise ValueError("新密码不能与旧密码一致")

    hashed = get_password_hash(new_password)
    user.password_hash = hashed
    user.password_updated_at = datetime.utcnow()

    await user_repo.add_password_history(
        session,
        user_id=user.id,
        password_hash=hashed,
        changed_by=changed_by or user.id,
    )


async def save_avatar(
    session: AsyncSession,
    user: User,
    file: UploadFile,
) -> str:
    suffix = Path(file.filename or "").suffix.lower() or ".png"
    avatar_dir = Path(settings.media_path) / "avatars"
    avatar_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{user.id}_{uuid4().hex}{suffix}"
    file_path = avatar_dir / filename

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    relative_url = f"{settings.media_url}/avatars/{filename}"
    user.avatar_url = relative_url
    await session.flush()
    return relative_url


async def record_login(
    session: AsyncSession,
    *,
    user_id: int,
    ip_address: Optional[str],
    user_agent: Optional[str],
    token_id: Optional[str],
) -> None:
    await user_repo.create_login_log(
        session,
        user_id=user_id,
        login_at=datetime.utcnow(),
        ip_address=ip_address,
        user_agent=user_agent,
        device_name=None,
        location=None,
        successful=True,
        token_id=token_id,
    )


async def record_logout(session: AsyncSession, token_id: str) -> None:
    await user_repo.mark_logout_at(session, token_id, datetime.utcnow())
