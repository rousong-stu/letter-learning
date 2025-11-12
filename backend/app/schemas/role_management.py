from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, constr


class RoleListItem(BaseModel):
    id: int
    role: str
    description: Optional[str] = None
    btnRolesCheckedList: List[str] = Field(default_factory=list)
    menuPermissions: List[str] = Field(default_factory=list)
    isSystem: int


class RoleListData(BaseModel):
    list: List[RoleListItem]
    total: int


class RoleEditRequest(BaseModel):
    id: Optional[int] = None
    role: constr(strip_whitespace=True, min_length=2, max_length=64)
    description: Optional[str] = None
    menuPermissions: List[str] = Field(default_factory=list)
    btnRolesCheckedList: List[str] = Field(default_factory=list)


class RoleDeleteRequest(BaseModel):
    ids: constr(strip_whitespace=True, min_length=1)


class RoleOption(BaseModel):
    id: int
    slug: str
    name: str
    description: Optional[str] = None
    isSystem: int = Field(alias="is_system")
