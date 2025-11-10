from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ProfileUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    displayName: Optional[str] = Field(None, alias="display_name")
    email: Optional[str]
    phone: Optional[str]
    gender: int
    birthday: Optional[date]
    locale: Optional[str]
    timezone: Optional[str]
    signature: Optional[str]
    avatarUrl: Optional[str] = Field(None, alias="avatar_url")
    passwordUpdatedAt: Optional[datetime] = Field(
        None, alias="password_updated_at"
    )
    createdAt: datetime = Field(alias="created_at")
    updatedAt: datetime = Field(alias="updated_at")


class ProfileDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    realName: Optional[str] = Field(None, alias="real_name")
    idNumber: Optional[str] = Field(None, alias="id_number")
    address: Optional[str]
    wechat: Optional[str]
    qq: Optional[str]
    linkedin: Optional[str]
    website: Optional[str]
    bio: Optional[str]


class LoginLogItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    loginAt: datetime = Field(alias="login_at")
    ipAddress: Optional[str] = Field(None, alias="ip_address")
    userAgent: Optional[str] = Field(None, alias="user_agent")
    deviceName: Optional[str] = Field(None, alias="device_name")
    location: Optional[str]
    successful: bool
    logoutAt: Optional[datetime] = Field(None, alias="logout_at")


class ProfileResponse(BaseModel):
    user: ProfileUser
    profile: ProfileDetail
    loginLogs: List[LoginLogItem]
    roles: List[str]


class ProfileUpdateRequest(BaseModel):
    displayName: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[int] = None
    birthday: Optional[date] = None
    locale: Optional[str] = None
    timezone: Optional[str] = None
    signature: Optional[str] = None

    realName: Optional[str] = None
    idNumber: Optional[str] = None
    address: Optional[str] = None
    wechat: Optional[str] = None
    qq: Optional[str] = None
    linkedin: Optional[str] = None
    website: Optional[str] = None
    bio: Optional[str] = None


class PasswordChangeRequest(BaseModel):
    oldPassword: str
    newPassword: str
    confirmPassword: str


class AvatarUploadResponse(BaseModel):
    avatarUrl: str
