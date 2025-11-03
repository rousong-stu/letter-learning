from __future__ import annotations

from typing import Any

from fastapi.responses import JSONResponse


def success_response(data: Any | None = None, msg: str = "操作成功") -> JSONResponse:
    return JSONResponse(status_code=200, content={"code": 200, "msg": msg, "data": data})


def error_response(
    msg: str,
    *,
    code: int = 400,
    data: Any | None = None,
    status_code: int = 200,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "code": code,
            "msg": msg,
            "data": data,
        },
    )

