from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import bcrypt
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError

from app.core.config import get_settings

settings = get_settings()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """校验密码明文与哈希是否匹配。"""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except ValueError:
        return False


def get_password_hash(password: str) -> str:
    """生成密码哈希。"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def create_access_token(
    subject: str | int,
    *,
    expires_delta: timedelta | None = None,
    additional_claims: dict | None = None,
) -> tuple[str, str, datetime]:
    """创建访问令牌，返回 (token, jti, 过期时间)。"""
    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta
        else timedelta(minutes=settings.access_token_expire_minutes)
    )
    token_id = uuid4().hex
    to_encode: dict = {"sub": str(subject), "exp": expire, "jti": token_id}
    if additional_claims:
        to_encode.update(additional_claims)
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    return encoded_jwt, token_id, expire


def decode_token(token: str, *, verify_exp: bool = True) -> dict:
    """解析 JWT，默认校验过期时间。"""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            options={"verify_exp": verify_exp},
        )
    except ExpiredSignatureError as exc:
        raise ValueError("令牌已过期") from exc
    except JWTError as exc:
        raise ValueError("令牌无效") from exc
    return payload
