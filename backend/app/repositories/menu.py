from __future__ import annotations

from typing import Iterable, Sequence

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Menu


async def list_menus(session: AsyncSession) -> Sequence[Menu]:
    stmt = (
        select(Menu)
        .options(selectinload(Menu.children))
        .order_by(Menu.order_no, Menu.id)
    )
    result = await session.execute(stmt)
    return result.scalars().unique().all()


async def get_menu_by_id(session: AsyncSession, menu_id: int) -> Menu | None:
    stmt = select(Menu).where(Menu.id == menu_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_menu_by_path(session: AsyncSession, path: str) -> Menu | None:
    stmt = select(Menu).where(Menu.path == path)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_menu(
    session: AsyncSession,
    *,
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
) -> Menu:
    menu = Menu(
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
    )
    session.add(menu)
    await session.flush()
    await session.refresh(menu)
    return menu


async def update_menu(session: AsyncSession, menu: Menu, **fields) -> Menu:
    for key, value in fields.items():
        setattr(menu, key, value)
    await session.flush()
    await session.refresh(menu)
    return menu


async def delete_menus(session: AsyncSession, ids: Iterable[int]) -> int:
    stmt = delete(Menu).where(Menu.id.in_(list(ids)))
    result = await session.execute(stmt)
    await session.flush()
    return result.rowcount or 0

