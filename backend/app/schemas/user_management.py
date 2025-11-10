from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, constr


class UserListItem(BaseModel):
    id: int
    username: str
    email: Optional[str]
    roles: List[str]
    datatime: str


class UserListData(BaseModel):
    list: List[UserListItem]
    total: int


class UserEditRequest(BaseModel):
    id: Optional[int] = Field(None, description="用户 ID，存在则更新")
    username: constr(strip_whitespace=True, min_length=1)
    password: Optional[constr(strip_whitespace=True, min_length=1)] = None
    email: Optional[str] = None
    roles: List[str] = Field(default_factory=list)


class UserDeleteRequest(BaseModel):
    ids: constr(strip_whitespace=True, min_length=1)
