from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import random
import string
import time
import asyncio
from datetime import date, datetime

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import get_settings
from app.core.dependencies import get_current_user, get_token_credentials
from app.core.database import AsyncSessionLocal, get_db
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
settings = get_settings()
logger = logging.getLogger(__name__)


def _gen_captcha_code(length: int = 4) -> str:
    pool = string.ascii_uppercase + string.digits
    return "".join(random.choice(pool) for _ in range(length))


def _captcha_token(code: str, ttl_seconds: int = 300) -> str:
    payload = {
        "c": code,
        "exp": int(time.time()) + ttl_seconds,
    }
    raw = json.dumps(payload, separators=(",", ":")).encode()
    sig = hmac.new(settings.jwt_secret.encode(), raw, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(raw + sig).decode()


def _verify_captcha(token: str, code: str) -> bool:
    try:
        data = base64.urlsafe_b64decode(token.encode())
        raw, sig = data[:-32], data[-32:]
        expected = hmac.new(settings.jwt_secret.encode(), raw, hashlib.sha256).digest()
        if not hmac.compare_digest(sig, expected):
            return False
        payload = json.loads(raw.decode())
        if payload.get("exp", 0) < time.time():
            return False
        return payload.get("c", "").upper() == code.upper()
    except Exception:
        return False


def _captcha_svg(code: str) -> str:
    colors = ["#3d8cff", "#10c469", "#f6c343", "#ff7b1b"]
    fill = random.choice(colors)
    svg = f"""<svg xmlns='http://www.w3.org/2000/svg' width='120' height='44'>
    <rect width='120' height='44' rx='10' ry='10' fill='rgba(255,255,255,0.9)' stroke='none'/>
    <text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle'
          font-family='Inter,Arial,sans-serif' font-size='22' font-weight='700' fill='{fill}'>{code}</text>
    </svg>"""
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def _should_auto_generate_story(last_login_at: datetime | None) -> bool:
    if not last_login_at:
        return True
    try:
        return last_login_at.date() != date.today()
    except Exception:
        return True


async def _auto_generate_story(
    user_id: int, session_factory: async_sessionmaker[AsyncSession] | None = None
) -> None:
    factory = session_factory or AsyncSessionLocal
    async with factory() as session:
        user = await session.get(User, user_id)
        if not user:
            return
        try:
            await word_story_service.generate_story(
                session,
                user,
                story_date=date.today(),
                force=True,
            )
            await session.commit()
        except WordStoryGenerationError as exc:
            await session.rollback()
            logger.warning("Auto regenerate story failed: %s", exc)
        except Exception:
            await session.rollback()
            logger.exception("Unexpected error when auto regenerating story")


@router.post("/login")
async def login(
    payload: LoginRequest,
    request: Request,
    session: AsyncSession = Depends(get_db),
) -> JSONResponse:
    if not _verify_captcha(payload.captcha_token, payload.captcha_code):
        return error_response("验证码错误或已过期", code=400)
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
        await session.commit()
    except Exception:
        await session.rollback()
        raise

    if should_auto_generate:
        bind = session.bind
        session_factory = (
            async_sessionmaker(bind, expire_on_commit=False, class_=AsyncSession)
            if bind is not None
            else AsyncSessionLocal
        )
        asyncio.create_task(
            _auto_generate_story(
                user.id,
                session_factory,
            )
        )

    return success_response(TokenData(token=token).model_dump(), msg="登录成功")


@router.get("/captcha")
async def get_captcha() -> JSONResponse:
    code = _gen_captcha_code()
    token = _captcha_token(code)
    image = _captcha_svg(code)
    return success_response({"captchaToken": token, "image": image})


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
