from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.database import get_db
from app.models import User
from app.schemas.profile import (
    AvatarUploadResponse,
    PasswordChangeRequest,
    ProfileResponse,
    ProfileUpdateRequest,
    ProfileUser,
    ProfileDetail,
    LoginLogItem,
)
from app.services import profile as profile_service
from app.utils.response import error_response, success_response
from app.repositories import user as user_repo

router = APIRouter(prefix="/profile", tags=["个人中心"])


@router.get("/me")
async def get_me(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    user, profile, logs = await profile_service.get_profile(
        session, current_user.id, log_limit=10
    )
    user_schema = ProfileUser.model_validate(user, from_attributes=True)
    profile_schema = ProfileDetail.model_validate(profile, from_attributes=True)
    log_schemas = [
        LoginLogItem.model_validate(
            {
                **log.__dict__,
                "successful": bool(log.successful),
            },
            from_attributes=True,
        )
        for log in logs
    ]
    data = ProfileResponse(
        user=user_schema,
        profile=profile_schema,
        loginLogs=log_schemas,
    )
    return success_response(data.model_dump(mode="json"), msg="获取成功")


@router.put("/me")
async def update_me(
    payload: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    try:
        updated_user = await profile_service.update_profile(
            session, current_user, payload.model_dump(exclude_unset=True)
        )
        await session.commit()
    except ValueError as exc:
        await session.rollback()
        return error_response(str(exc), code=400)
    except Exception:
        await session.rollback()
        raise

    refreshed_user = await user_repo.get_user_by_id(session, updated_user.id)
    if not refreshed_user:
        return error_response("用户不存在", code=404)
    profile_obj = refreshed_user.profile or await user_repo.upsert_user_profile(
        session, refreshed_user.id, {}
    )

    user_schema = ProfileUser.model_validate(
        refreshed_user, from_attributes=True
    )
    profile_schema = ProfileDetail.model_validate(
        profile_obj, from_attributes=True
    )
    data = {
        "user": user_schema.model_dump(mode="json"),
        "profile": profile_schema.model_dump(mode="json"),
    }
    return success_response(data, msg="保存成功")


@router.post("/password")
async def change_password(
    payload: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    if payload.newPassword != payload.confirmPassword:
        return error_response("两次输入的新密码不一致", code=400)

    try:
        await profile_service.change_password(
            session,
            current_user,
            old_password=payload.oldPassword,
            new_password=payload.newPassword,
        )
        await session.commit()
    except ValueError as exc:
        await session.rollback()
        return error_response(str(exc), code=400)
    except Exception:
        await session.rollback()
        raise

    return success_response(msg="密码修改成功，请重新登录")


@router.post("/avatar", response_model=AvatarUploadResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    if file.content_type not in {"image/png", "image/jpeg", "image/jpg", "image/webp"}:
        return error_response("仅支持 PNG/JPG/WEBP 图片", code=400)
    try:
        url = await profile_service.save_avatar(session, current_user, file)
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    return success_response(
        AvatarUploadResponse(avatarUrl=url).model_dump(), msg="头像更新成功"
    )


@router.get("/loginLogs")
async def login_logs(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    logs = await user_repo.list_login_logs(session, current_user.id, limit=limit)
    log_schemas = [
        LoginLogItem.model_validate(
            {
                **log.__dict__,
                "successful": bool(log.successful),
            },
            from_attributes=True,
        ).model_dump(mode="json")
        for log in logs
    ]
    return success_response({"list": log_schemas}, msg="获取成功")
