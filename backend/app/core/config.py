from functools import lru_cache

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """全局配置加载器，负责读取环境变量。"""

    app_name: str = "LetterLearning"
    app_env: str = "development"
    app_debug: bool = True

    db_user: str
    db_password: str
    db_host: str = "127.0.0.1"
    db_port: int = 3306
    db_name: str

    redis_url: str | None = None

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30

    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @computed_field
    def database_url(self) -> str:
        """返回同步连接串，供 Alembic 或运维脚本使用。"""
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @computed_field
    def async_database_url(self) -> str:
        """返回异步连接串，供应用运行时使用。"""
        return (
            f"mysql+aiomysql://{self.db_user}:{self.db_password}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
        )


@lru_cache
def get_settings() -> Settings:
    """以单例形式提供配置对象。"""
    return Settings()

