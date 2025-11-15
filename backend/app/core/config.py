from functools import lru_cache
from pathlib import Path

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
    media_directory: str = "uploads"
    media_url: str = "/static"

    coze_api_base: str = "https://api.coze.cn"
    coze_api_token: str | None = None
    coze_bot_id: str | None = None
    coze_workflow_id: str | None = "7572622349360758824"
    coze_user_prefix: str = "ll-user"
    coze_chat_bot_id: str | None = "7571082057812967487"
    coze_chat_space_id: str | None = "7558388129191739455"
    coze_poll_interval_seconds: float = 1.2
    coze_poll_timeout_seconds: int = 90
    coze_request_timeout_seconds: int = 60

    merriam_dictionary_api_key: str | None = "015c5134-71dc-4766-9b63-69aa5c2bec51"
    merriam_thesaurus_api_key: str | None = "fbd67380-1208-4f60-93a5-ac4758820145"
    dictionary_api_timeout_seconds: float = 15.0
    dictionary_translation_bot_id: str | None = "7572629275527348260"
    dictionary_translation_space_id: str | None = "7558388129191739455"

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

    @computed_field
    def media_path(self) -> str:
        base_path = Path(__file__).resolve().parents[2]
        return str((base_path / self.media_directory).resolve())


@lru_cache
def get_settings() -> Settings:
    """以单例形式提供配置对象。"""
    return Settings()
