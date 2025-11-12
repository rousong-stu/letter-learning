from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import User
from app.schemas.menu import MenuDeleteRequest, MenuEditRequest
from app.services import menu as menu_service
from app.utils.response import error_response, success_response

router = APIRouter()


@router.get("/menuManagement/getTree")
async def get_menu_tree(
    _current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    tree = await menu_service.get_menu_tree(session)
    return success_response({"list": tree}, msg="获取成功")


@router.post("/menuManagement/doEdit")
async def save_menu(
    payload: MenuEditRequest,
    _current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    try:
        menu = await menu_service.save_menu(
            session,
            menu_id=payload.id,
            parent_id=payload.parentId,
            title=payload.title,
            path=payload.path,
            component=payload.component,
            icon=payload.icon,
            menu_type=payload.type,
            order_no=payload.orderNo,
            is_external=payload.isExternal,
            is_cache=payload.isCache,
            is_hidden=payload.isHidden,
            redirect=payload.redirect,
            status=payload.status,
            role_slugs=payload.roles,
        )
        await session.commit()
    except menu_service.MenuOperationError as exc:
        await session.rollback()
        return error_response(str(exc), code=400)
    except Exception:
        await session.rollback()
        raise

    return success_response({"id": menu.id}, msg="保存成功")


@router.post("/menuManagement/doDelete")
async def delete_menu(
    payload: MenuDeleteRequest,
    _current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    try:
        ids = [int(part) for part in payload.ids.split(",") if part.strip()]
    except ValueError:
        return error_response("参数格式错误", code=400)

    if not ids:
        return error_response("未提供有效的菜单ID", code=400)

    deleted = await menu_service.delete_menus(session, ids)
    await session.commit()
    if deleted == 0:
        return error_response("未找到要删除的菜单", code=404)
    return success_response(msg="删除成功")


@router.get("/menu/routes")
async def menu_routes(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    menus = await menu_service.get_menus_for_user(session, current_user)

    def relative_path(path: str | None, parent_path: str | None) -> str:
        if not path:
            return ""
        path = path.strip()
        if not parent_path or parent_path in ("", "/"):
            return path.lstrip("/")
        parent_norm = parent_path.rstrip("/").lstrip("/")
        path_norm = path.lstrip("/")
        if parent_norm and path_norm.startswith(parent_norm + "/"):
            remainder = path_norm[len(parent_norm) + 1 :]
            return remainder or ""
        return path_norm

    def to_route(node, parent_path: str | None):
        if node["type"] == "button":
            return None
        route_path = relative_path(node["path"], parent_path)
        if not route_path:
            # fallback to last segment or id
            route_path = (node["path"] or "").strip("/").split("/")[-1] or f"menu-{node['id']}"
        meta = {
            "title": node["title"],
            "icon": node["icon"],
            "hidden": bool(node["is_hidden"]),
            "noKeepAlive": not bool(node["is_cache"]),
        }
        children = [
            child for child in (to_route(child, node["path"]) for child in node["children"]) if child
        ]
        route = {
            "path": route_path,
            "name": f"Menu{node['id']}",
            "component": "Layout" if node["type"] == "catalog" else node["component"],
            "redirect": (
                relative_path(node["redirect"], node["path"]) if node["redirect"] else None
            ),
            "meta": meta,
        }
        if children:
            route["children"] = children
        return route

    children_routes = [route for route in (to_route(item, "/") for item in menus) if route]
    if not children_routes:
        return success_response({"list": []}, msg="获取成功")

    def first_accessible_path(routes):
        for route in routes:
            if route["meta"].get("hidden"):
                continue
            return "/" + route["path"].lstrip("/")
        return "/" + routes[0]["path"].lstrip("/")

    root_route = {
        "path": "/",
        "name": "RootLayout",
        "component": "Layout",
        "redirect": first_accessible_path(children_routes),
        "meta": {"hidden": True},
        "children": children_routes,
    }
    return success_response({"list": [root_route]}, msg="获取成功")
