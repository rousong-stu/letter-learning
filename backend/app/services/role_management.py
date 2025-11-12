from __future__ import annotations

from typing import Iterable

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import role as role_repo


class RoleOperationError(ValueError):
    """用于抛出业务错误。"""


async def paginate_roles(
    session: AsyncSession,
    *,
    keyword: str | None,
    page_no: int,
    page_size: int,
):
    offset = (page_no - 1) * page_size
    roles = await role_repo.list_roles(
        session,
        keyword=keyword,
        offset=offset,
        limit=page_size,
    )
    total = await role_repo.count_roles(session, keyword=keyword)
    return list(roles), total


async def create_role(
    session: AsyncSession,
    *,
    slug: str,
    description: str | None,
    menu_permissions: Iterable[str],
    action_permissions: Iterable[str],
):
    slug = slug.strip()
    if await role_repo.get_role_by_slug(session, slug):
        raise RoleOperationError("角色码已存在")
    role = await role_repo.create_role(
        session,
        slug=slug,
        name=slug,
        description=description,
        is_system=0,
    )
    await role_repo.replace_role_permissions(
        session,
        role_id=role.id,
        menu_permissions=menu_permissions,
        action_permissions=action_permissions,
    )
    await session.refresh(role)
    return role


async def update_role(
    session: AsyncSession,
    *,
    role_id: int,
    slug: str,
    description: str | None,
    menu_permissions: Iterable[str],
    action_permissions: Iterable[str],
):
    role = await role_repo.get_role_by_id(session, role_id)
    if not role:
        raise RoleOperationError("角色不存在")
    if role.is_system:
        raise RoleOperationError("系统内置角色不可编辑")
    slug = slug.strip()
    existing = await role_repo.get_role_by_slug(session, slug)
    if existing and existing.id != role_id:
        raise RoleOperationError("角色码已存在")
    await role_repo.update_role(
        session,
        role,
        slug=slug,
        name=slug,
        description=description,
    )
    await role_repo.replace_role_permissions(
        session,
        role_id=role.id,
        menu_permissions=menu_permissions,
        action_permissions=action_permissions,
    )
    await session.refresh(role)
    return role


async def delete_roles(session: AsyncSession, role_ids: Iterable[int]) -> int:
    roles = []
    for role_id in role_ids:
        role = await role_repo.get_role_by_id(session, role_id)
        if role:
            roles.append(role)
    system_ids = [role.id for role in roles if role.is_system]
    if system_ids:
        raise RoleOperationError("系统内置角色不可删除")
    return await role_repo.delete_roles(session, role_ids)


async def list_role_options(session: AsyncSession):
    roles = await role_repo.list_all_roles(session)
    return roles
