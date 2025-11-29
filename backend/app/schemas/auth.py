from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    captcha_code: str = Field(
        ..., alias="captchaCode", description="验证码文本（必填）"
    )
    captcha_token: str = Field(
        ..., alias="captchaToken", description="验证码令牌（必填）"
    )

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "examples": [
                {
                    "username": "admin",
                    "password": "123456",
                    "captchaCode": "ABCD",
                    "captchaToken": "base64-token",
                }
            ]
        },
    }


class RegisterRequest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    password_confirm: str = Field(..., alias="passwordConfirm", description="确认密码")
    invite_code: str = Field(..., alias="inviteCode", description="邀请码")
    email: EmailStr = Field(..., description="邮箱")

    model_config = {"populate_by_name": True, "json_schema_extra": {"examples": [
        {
            "username": "new_user",
            "password": "123456",
            "passwordConfirm": "123456",
            "inviteCode": "letter-learning",
            "email": "new_user@example.com",
        }
    ]}}


class TokenData(BaseModel):
    token: str


class UserInfoData(BaseModel):
    username: str
    avatar: str
