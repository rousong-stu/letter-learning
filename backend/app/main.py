from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as api_v1_router
from app.core.config import get_settings
from app.core.database import async_engine

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """控制应用生命周期，保证数据库连接及时关闭。"""
    yield
    await async_engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        debug=settings.app_debug,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_v1_router)

    @app.get("/", tags=["系统"], summary="根路径探活")
    async def root() -> dict[str, str]:
        return {"message": "Letter Learning API 正常运行"}

    return app


app = create_app()

