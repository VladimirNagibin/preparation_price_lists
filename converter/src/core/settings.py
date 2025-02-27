import os
from logging import config as logging_config

from pydantic_settings import BaseSettings, SettingsConfigDict

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )
    PROJECT_NAME: str = "project"
    APP_RELOAD: bool = True
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    UPLOAD_DIR: str = os.path.join("data", "upload")
    TTL: int = 60 * 60 * 6  # TTL in seconds
    CHUNK: int = 1024
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    LOAD: int = 0
    CONVERTED: int = 1


settings = Settings()
