from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import User
from app.schemas.role_management import (
    RoleDeleteRequest,
    RoleEditRequest,
    RoleListData,
    RoleListItem,
    RoleOption,
)
from app.services import role_management as role_service
from app.utils.response import error_response, success_response

router = APIRouter()


def _serialize_role(role) -> RoleListItem:
    menu_permissions = [
        perm.permission_value
        for perm in role.permissions
        if perm.permission_type == "menu"
    ]
    action_permissions = [
        perm.permission_value
        for perm in role.permissions
        if perm.permission_type == "action"
    ]
    return RoleListItem(
        id=role.id,
        role=role.slug,
        description=role.description,
        btnRolesCheckedList=action_permissions,
        menuPermissions=menu_permissions,
        isSystem=role.is_system,
    )


@router.get("/roleManagement/getList")
async def get_role_list(
    page_no: int = Query(1, alias="pageNo", ge=1),
    page_size: int = Query(10, alias="pageSize", ge=1, le=100),
    role: str | None = Query(None),
    _current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    roles, total = await role_service.paginate_roles(
        session, keyword=role, page_no=page_no, page_size=page_size
    )
    data = RoleListData(
        list=[_serialize_role(item) for item in roles],
        total=total,
    )
    return success_response(data.model_dump(mode="json"), msg="获取成功")


@router.post("/roleManagement/doEdit")
async def edit_role(
    payload: RoleEditRequest,
    _current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    try:
        if payload.id:
            role = await role_service.update_role(
                session,
                role_id=payload.id,
                slug=payload.role,
                description=payload.description,
                menu_permissions=payload.menuPermissions,
                action_permissions=payload.btnRolesCheckedList,
            )
        else:
            role = await role_service.create_role(
                session,
                slug=payload.role,
                description=payload.description,
                menu_permissions=payload.menuPermissions,
                action_permissions=payload.btnRolesCheckedList,
            )
        await session.commit()
    except role_service.RoleOperationError as exc:
        await session.rollback()
        return error_response(str(exc), code=400)
    except Exception:
        await session.rollback()
        raise

    return success_response({"id": role.id}, msg="保存成功")


@router.post("/roleManagement/doDelete")
async def delete_role(
    payload: RoleDeleteRequest,
    _current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    try:
        id_list = [int(part) for part in payload.ids.split(",") if part.strip()]
    except ValueError:
        return error_response("参数格式错误", code=400)

    if not id_list:
        return error_response("未提供有效的角色ID", code=400)

    try:
        deleted = await role_service.delete_roles(session, id_list)
        await session.commit()
    except role_service.RoleOperationError as exc:
        await session.rollback()
        return error_response(str(exc), code=400)
    except Exception:
        await session.rollback()
        raise

    if deleted == 0:
        return error_response("未找到要删除的角色", code=404)

    return success_response(msg="删除成功")


@router.get("/roleManagement/options")
async def role_options(
    _current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    roles = await role_service.list_role_options(session)
    data = [
        RoleOption.model_validate(role, from_attributes=True).model_dump(
            by_alias=True
        )
        for role in roles
    ]
    return success_response({"list": data}, msg="获取成功")
