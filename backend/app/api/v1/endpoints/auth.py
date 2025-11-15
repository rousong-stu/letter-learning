from __future__ import annotations

import logging
from datetime import date, datetime

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_token_credentials
from app.core.database import get_db
from app.core.security import decode_token
from app.models import User
from app.repositories import token as token_repo
from app.schemas.auth import LoginRequest, RegisterRequest, TokenData, UserInfoData
from app.services import auth as auth_service
from app.services import profile as profile_service
from app.services import word_story as word_story_service
from app.services.word_story import WordStoryGenerationError
from app.utils.response import error_response, success_response

router = APIRouter()
DEFAULT_AVATAR = (
    "https://i.gtimg.cn/club/item/face/img/2/15922_100.gif"
)  # 与前端默认头像保持一致
INVITE_CODE = "letter-learning"
logger = logging.getLogger(__name__)


def _should_auto_generate_story(last_login_at: datetime | None) -> bool:
    if not last_login_at:
        return True
    try:
        return last_login_at.date() != date.today()
    except Exception:
        return True


async def _auto_generate_story(session: AsyncSession, user: User) -> None:
    try:
        await word_story_service.generate_story(
            session,
            user,
            story_date=date.today(),
            force=True,
        )
    except WordStoryGenerationError as exc:
        logger.warning("Auto regenerate story failed: %s", exc)
    except Exception:
        logger.exception("Unexpected error when auto regenerating story")


@router.post("/login")
async def login(
    payload: LoginRequest,
    request: Request,
    session: AsyncSession = Depends(get_db),
) -> JSONResponse:
    try:
        user = await auth_service.authenticate_user(
            session,
            username=payload.username,
            password=payload.password,
        )
    except ValueError as exc:
        return error_response(str(exc), code=403)

    if not user:
        return error_response("用户名或密码错误", code=401)

    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None
    should_auto_generate = _should_auto_generate_story(user.last_login_at)

    try:
        token, refresh_token_record = await auth_service.issue_token_pair(
            session,
            user=user,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        await profile_service.record_login(
            session,
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            token_id=refresh_token_record.token,
        )
        if should_auto_generate:
            await _auto_generate_story(session, user)
        await session.commit()
    except Exception:
        await session.rollback()
        raise

    return success_response(TokenData(token=token).model_dump(), msg="登录成功")


@router.post("/register")
async def register(
    payload: RegisterRequest,
    request: Request,
    session: AsyncSession = Depends(get_db),
) -> JSONResponse:
    if payload.password != payload.password_confirm:
        return error_response("两次输入的密码不一致", code=400)
    if payload.invite_code.strip() != INVITE_CODE:
        return error_response("邀请码不正确", code=400)
    if not payload.email:
        return error_response("邮箱不能为空", code=400)
    try:
        user = await auth_service.register_user(
            session,
            username=payload.username,
            password=payload.password,
            email=payload.email,
        )
        user_agent = request.headers.get("user-agent")
        ip_address = request.client.host if request.client else None
        token, _ = await auth_service.issue_token_pair(
            session,
            user=user,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        await session.commit()
    except ValueError as exc:
        await session.rollback()
        return error_response(str(exc), code=400)
    except Exception:
        await session.rollback()
        raise

    return success_response(TokenData(token=token).model_dump(), msg="注册成功")


@router.get("/userInfo")
async def user_info(current_user: User = Depends(get_current_user)) -> JSONResponse:
    data = UserInfoData(
        username=current_user.display_name or current_user.username,
        avatar=current_user.avatar_url or DEFAULT_AVATAR,
    )
    return success_response(data.model_dump(), msg="获取成功")


@router.get("/logout")
async def logout(
    token: str = Depends(get_token_credentials),
    _current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> JSONResponse:
    try:
        payload = decode_token(token)
    except ValueError:
        return success_response(msg="退出成功")

    token_id = payload.get("jti")
    if token_id:
        try:
            await auth_service.revoke_token(session, token_id)
            await profile_service.record_logout(session, token_id)
            await session.commit()
        except Exception:
            await session.rollback()
            raise

    return success_response(msg="退出成功")


@router.get("/refreshToken")
async def refresh_token(
    token: str = Depends(get_token_credentials),
    session: AsyncSession = Depends(get_db),
) -> JSONResponse:
    try:
        payload = decode_token(token, verify_exp=False)
    except ValueError as exc:
        return error_response(str(exc), code=401)

    user_id = payload.get("sub")
    token_id = payload.get("jti")
    if not user_id or not token_id:
        return error_response("令牌格式不正确", code=401)

    record = await token_repo.get_refresh_token(session, token_id)
    if not record or record.revoked_at is not None:
        return error_response("刷新凭证已失效，请重新登录", code=401)
    if record.expires_at < datetime.utcnow():
        return error_response("刷新凭证已过期，请重新登录", code=402)

    user = await session.get(User, int(user_id))
    if not user or user.status != 1:
        return error_response("用户不存在或已禁用", code=403)

    try:
        await auth_service.revoke_token(session, token_id)
        token_value, _ = await auth_service.issue_token_pair(
            session,
            user=user,
            user_agent=None,
            ip_address=None,
        )
        await session.commit()
    except Exception:
        await session.rollback()
        raise

    return success_response(TokenData(token=token_value).model_dump(), msg="刷新Token成功")


@router.get("/expireToken")
async def expire_token(token: str = Depends(get_token_credentials)) -> JSONResponse:
    try:
        decode_token(token)
    except ValueError as exc:
        if str(exc) == "令牌已过期":
            return error_response("令牌已过期", code=402)
        return error_response(str(exc), code=401)
    return success_response(msg="令牌未过期")
