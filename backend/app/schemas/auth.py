from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


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
