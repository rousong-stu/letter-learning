from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import RefreshToken


async def create_refresh_token(
    session: AsyncSession,
    *,
    user_id: int,
    token_id: str,
    expires_at: datetime,
    user_agent: str | None = None,
    ip_address: str | None = None,
) -> RefreshToken:
    record = RefreshToken(
        user_id=user_id,
        token=token_id,
        expires_at=expires_at,
        user_agent=user_agent,
        ip_address=ip_address,
    )
    session.add(record)
    await session.flush()
    return record


async def revoke_refresh_token(session: AsyncSession, token_id: str) -> None:
    stmt = (
        update(RefreshToken)
        .where(RefreshToken.token == token_id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=datetime.utcnow())
    )
    await session.execute(stmt)


async def get_refresh_token(
    session: AsyncSession, token_id: str
) -> Optional[RefreshToken]:
    stmt = select(RefreshToken).where(RefreshToken.token == token_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

