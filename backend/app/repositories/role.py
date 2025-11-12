from __future__ import annotations

from typing import Iterable, Sequence

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Role, RolePermission


async def list_roles(
    session: AsyncSession,
    *,
    keyword: str | None,
    offset: int,
    limit: int,
) -> Sequence[Role]:
    stmt = (
        select(Role)
        .options(selectinload(Role.permissions))
        .order_by(Role.id.desc())
        .offset(offset)
        .limit(limit)
    )
    if keyword:
        stmt = stmt.where(Role.slug.like(f"%{keyword}%"))
    result = await session.execute(stmt)
    return result.scalars().all()


async def count_roles(session: AsyncSession, *, keyword: str | None) -> int:
    stmt = select(func.count(Role.id))
    if keyword:
        stmt = stmt.where(Role.slug.like(f"%{keyword}%"))
    result = await session.execute(stmt)
    return result.scalar_one()


async def list_all_roles(session: AsyncSession) -> Sequence[Role]:
    stmt = select(Role).order_by(Role.id)
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_role_by_id(session: AsyncSession, role_id: int) -> Role | None:
    stmt = select(Role).options(selectinload(Role.permissions)).where(Role.id == role_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_role_by_slug(session: AsyncSession, slug: str) -> Role | None:
    stmt = select(Role).where(Role.slug == slug)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_role(
    session: AsyncSession,
    *,
    slug: str,
    name: str,
    description: str | None = None,
    is_system: int = 0,
) -> Role:
    role = Role(
        slug=slug,
        name=name,
        description=description,
        is_system=is_system,
    )
    session.add(role)
    await session.flush()
    await session.refresh(role)
    return role


async def update_role(
    session: AsyncSession,
    role: Role,
    *,
    slug: str,
    name: str,
    description: str | None,
) -> Role:
    role.slug = slug
    role.name = name
    role.description = description
    await session.flush()
    await session.refresh(role)
    return role


async def replace_role_permissions(
    session: AsyncSession,
    *,
    role_id: int,
    menu_permissions: Iterable[str],
    action_permissions: Iterable[str],
) -> None:
    await session.execute(
        delete(RolePermission).where(RolePermission.role_id == role_id)
    )
    entries: list[RolePermission] = []
    for value in dict.fromkeys(menu_permissions or []):
        if not value:
            continue
        entries.append(
            RolePermission(
                role_id=role_id,
                permission_type="menu",
                permission_value=str(value),
            )
        )
    for value in dict.fromkeys(action_permissions or []):
        if not value:
            continue
        entries.append(
            RolePermission(
                role_id=role_id,
                permission_type="action",
                permission_value=str(value),
            )
        )
    session.add_all(entries)
    await session.flush()


async def delete_roles(session: AsyncSession, role_ids: Iterable[int]) -> int:
    stmt = delete(Role).where(Role.id.in_(list(role_ids)))
    result = await session.execute(stmt)
    await session.flush()
    return result.rowcount or 0
