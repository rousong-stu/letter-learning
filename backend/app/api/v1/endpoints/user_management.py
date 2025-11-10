from __future__ import annotations

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.user_management import (
    UserDeleteRequest,
    UserEditRequest,
    UserListData,
    UserListItem,
)
from app.services import user_management as user_service
from app.utils.response import error_response, success_response

router = APIRouter()


def _format_datetime(value: datetime | None) -> str:
    if not value:
        return ""
    return value.strftime("%Y-%m-%d %H:%M:%S")


@router.get("/userManagement/getList")
async def get_user_list(
    page_no: int = Query(1, alias="pageNo", ge=1),
    page_size: int = Query(10, alias="pageSize", ge=1, le=100),
    username: str | None = Query(None),
    session: AsyncSession = Depends(get_db),
):
    users, total = await user_service.paginate_users(
        session,
        username=username,
        page_no=page_no,
        page_size=page_size,
    )
    items: List[UserListItem] = []
    for user in users:
        items.append(
            UserListItem(
                id=user.id,
                username=user.username,
                email=user.email,
                roles=[role.slug for role in user.roles],
                datatime=_format_datetime(user.updated_at or user.created_at),
            )
        )
    data = UserListData(list=items, total=total)
    return success_response(data.model_dump(), msg="获取成功")


@router.post("/userManagement/doEdit")
async def edit_user(
    payload: UserEditRequest,
    session: AsyncSession = Depends(get_db),
):
    try:
        if payload.id:
            user = await user_service.update_user_with_roles(
                session,
                user_id=payload.id,
                username=payload.username,
                email=payload.email,
                password=payload.password,
                roles=payload.roles,
            )
        else:
            if not payload.password:
                return error_response("新增用户时需要填写密码", code=400)
            user = await user_service.create_user_with_roles(
                session,
                username=payload.username,
                password=payload.password,
                email=payload.email,
                roles=payload.roles,
            )
        await session.commit()
    except ValueError as exc:
        await session.rollback()
        return error_response(str(exc), code=400)
    except Exception:
        await session.rollback()
        raise

    return success_response(
        {"id": user.id},
        msg="保存成功",
    )


@router.post("/userManagement/doDelete")
async def delete_user(
    payload: UserDeleteRequest,
    session: AsyncSession = Depends(get_db),
):
    try:
        id_list = [int(part) for part in payload.ids.split(",") if part.strip()]
    except ValueError:
        return error_response("参数格式错误", code=400)

    if not id_list:
        return error_response("未提供有效的用户ID", code=400)

    try:
        deleted = await user_service.delete_users(session, id_list)
        await session.commit()
    except Exception:
        await session.rollback()
        raise

    if deleted == 0:
        return error_response("未找到要删除的用户", code=404)

    return success_response(msg="删除成功")
