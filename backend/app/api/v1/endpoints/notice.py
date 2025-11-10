from __future__ import annotations

from fastapi import APIRouter

from app.utils.response import success_response

router = APIRouter()


@router.get("/notice/getList", summary="公告列表占位")
async def get_notice_list():
    data = {"list": [], "total": 0}
    return success_response(data, msg="暂无公告数据")

