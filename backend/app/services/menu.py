from __future__ import annotations

from typing import Iterable, List, Mapping

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Role, RolePermission, User
from app.repositories import menu as menu_repo


class MenuOperationError(ValueError):
    pass


async def get_menu_tree(session: AsyncSession):
    menus = await menu_repo.list_menus(session)
    role_map = await _get_menu_role_map(session)
    return build_tree(menus, role_map=role_map)


def serialize_menu(menu, role_map: Mapping[int, list[str]] | None = None):
    return {
        "id": menu.id,
        "parent_id": menu.parent_id,
        "title": menu.title,
        "path": menu.path,
        "component": menu.component,
        "icon": menu.icon,
        "type": menu.type,
        "order_no": menu.order_no,
        "is_external": menu.is_external,
        "is_cache": menu.is_cache,
        "is_hidden": menu.is_hidden,
        "redirect": menu.redirect,
        "status": menu.status,
        "roles": (role_map or {}).get(menu.id, []),
    }


def build_tree(
    menus: List,
    allowed_ids: set[int] | None = None,
    role_map: Mapping[int, list[str]] | None = None,
) -> List:
    nodes = [serialize_menu(menu, role_map) for menu in menus if menu.status == 1]
    node_map = {node["id"]: node for node in nodes}
    for node in nodes:
        node["children"] = []
    for node in nodes:
        parent_id = node.get("parent_id")
        if parent_id and parent_id in node_map:
            node_map[parent_id]["children"].append(node)
    tree = [node for node in nodes if not node.get("parent_id")]
    if allowed_ids is None:
        return tree

    def filter_node(node):
        children = [child for child in node["children"] if filter_node(child)]
        node["children"] = children
        return node["id"] in allowed_ids or bool(children)

    return [node for node in tree if filter_node(node)]


async def save_menu(
    session: AsyncSession,
    *,
    menu_id: int | None,
    parent_id: int | None,
    title: str,
    path: str,
    component: str | None,
    icon: str | None,
    menu_type: str,
    order_no: int,
    is_external: int,
    is_cache: int,
    is_hidden: int,
    redirect: str | None,
    status: int,
    role_slugs: list[str],
):
    existing = await menu_repo.get_menu_by_path(session, path)
    if existing and (menu_id is None or existing.id != menu_id):
        raise MenuOperationError("菜单路径已存在")

    if menu_id:
        menu = await menu_repo.get_menu_by_id(session, menu_id)
        if not menu:
            raise MenuOperationError("菜单不存在")
        menu = await menu_repo.update_menu(
            session,
            menu,
            parent_id=parent_id,
            title=title,
            path=path,
            component=component,
            icon=icon,
            type=menu_type,
            order_no=order_no,
            is_external=is_external,
            is_cache=is_cache,
            is_hidden=is_hidden,
            redirect=redirect,
            status=status,
        )
        await _update_menu_roles(session, menu.id, role_slugs)
        return menu

    menu = await menu_repo.create_menu(
        session,
        parent_id=parent_id,
        title=title,
        path=path,
        component=component,
        icon=icon,
        menu_type=menu_type,
        order_no=order_no,
        is_external=is_external,
        is_cache=is_cache,
        is_hidden=is_hidden,
        redirect=redirect,
    )
    menu.status = status
    await session.flush()
    await session.refresh(menu)
    await _update_menu_roles(session, menu.id, role_slugs)
    return menu


async def delete_menus(session: AsyncSession, ids: Iterable[int]) -> int:
    str_ids = [str(i) for i in ids]
    await session.execute(
        delete(RolePermission).where(
            RolePermission.permission_type == "menu",
            RolePermission.permission_value.in_(str_ids),
        )
    )
    return await menu_repo.delete_menus(session, ids)


async def get_menus_for_user(session: AsyncSession, user: User):
    menus = await menu_repo.list_menus(session)
    if not menus:
        return []

    role_ids = {role.id for role in user.roles}
    result = await session.execute(
        select(RolePermission.permission_value, RolePermission.role_id).where(
            RolePermission.permission_type == "menu",
        )
    )
    permission_map: dict[int, set[int]] = {}
    for value, role_id in result.fetchall():
        if role_id is None or not str(value).isdigit():
            continue
        menu_id = int(str(value))
        permission_map.setdefault(menu_id, set()).add(role_id)

    allowed_ids: set[int] = set()
    for menu in menus:
        permissions = permission_map.get(menu.id)
        if not permissions:
            allowed_ids.add(menu.id)
            continue
        if role_ids and permissions.intersection(role_ids):
            allowed_ids.add(menu.id)

    if not allowed_ids:
        return []
    return build_tree(menus, allowed_ids=allowed_ids)


async def _update_menu_roles(
    session: AsyncSession, menu_id: int, role_slugs: list[str]
) -> None:
    await session.execute(
        delete(RolePermission).where(
            RolePermission.permission_type == "menu",
            RolePermission.permission_value == str(menu_id),
        )
    )
    if not role_slugs:
        return
    role_rows = await session.execute(
        select(Role.id, Role.slug).where(Role.slug.in_(role_slugs))
    )
    role_map = {slug: role_id for role_id, slug in role_rows}
    entries: list[RolePermission] = []
    for slug in dict.fromkeys(role_slugs):
        role_id = role_map.get(slug)
        if not role_id:
            continue
        entries.append(
            RolePermission(
                role_id=role_id,
                permission_type="menu",
                permission_value=str(menu_id),
            )
        )
    session.add_all(entries)
    await session.flush()


async def _get_menu_role_map(session: AsyncSession) -> dict[int, list[str]]:
    rows = await session.execute(
        select(RolePermission.permission_value, Role.slug)
        .join(Role, Role.id == RolePermission.role_id)
        .where(RolePermission.permission_type == "menu")
    )
    role_map: dict[int, list[str]] = {}
    for value, slug in rows.fetchall():
        if not str(value).isdigit():
            continue
        menu_id = int(value)
        role_map.setdefault(menu_id, []).append(slug)
    return role_map
