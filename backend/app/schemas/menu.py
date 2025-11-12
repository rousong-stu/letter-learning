from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, constr


class MenuTreeItem(BaseModel):
    id: int
    parentId: Optional[int] = Field(None, alias="parent_id")
    title: str
    path: str
    component: Optional[str] = None
    icon: Optional[str] = None
    type: str
    orderNo: int = Field(alias="order_no")
    isExternal: int = Field(alias="is_external")
    isCache: int = Field(alias="is_cache")
    isHidden: int = Field(alias="is_hidden")
    redirect: Optional[str] = None
    status: int
    children: List["MenuTreeItem"] = Field(default_factory=list)
    roles: List[str] = Field(default_factory=list)

    model_config = {
        "populate_by_name": True,
    }


class MenuEditRequest(BaseModel):
    id: Optional[int] = None
    parentId: Optional[int] = None
    title: constr(strip_whitespace=True, min_length=1, max_length=128)
    path: constr(strip_whitespace=True, min_length=1, max_length=255)
    component: Optional[str] = None
    icon: Optional[str] = None
    type: constr(strip_whitespace=True, min_length=3, max_length=16) = "menu"
    orderNo: int = 0
    isExternal: int = 0
    isCache: int = 0
    isHidden: int = 0
    redirect: Optional[str] = None
    status: int = 1
    roles: List[str] = Field(default_factory=list)


class MenuDeleteRequest(BaseModel):
    ids: str
