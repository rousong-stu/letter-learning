from fastapi import APIRouter

router = APIRouter()


@router.get("/health", summary="服务健康检查")
async def health_check() -> dict[str, str]:
    """返回服务状态，用于外部探活。"""
    return {"status": "ok"}

