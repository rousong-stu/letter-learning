from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class RegisterRequest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    phone: Optional[str] = Field(None, description="手机号")
    phone_code: Optional[str] = Field(None, alias="phoneCode", description="手机验证码")
    email: Optional[EmailStr] = Field(None, description="邮箱")

    model_config = {"populate_by_name": True}


class TokenData(BaseModel):
    token: str


class UserInfoData(BaseModel):
    username: str
    avatar: str
    roles: List[str]
    permissions: List[str]

