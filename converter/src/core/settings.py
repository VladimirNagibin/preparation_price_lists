import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )
    PROJECT_NAME: str = "converter"
    APP_RELOAD: bool = True
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    UPLOAD_DIR: str = os.path.join("data", "upload")
    TTL: int = 60 * 60 * 6  # TTL in seconds
    CHUNK: int = 1024
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    LOG_LEVEL: str = "INFO"
    LOAD: int = 0
    CONVERTED: int = 1
    LOGSTASH_HOST: str = "localhost"
    LOGSTASH_PORT: int = 5044
    LOGSTASH_HANDLER: bool = True


settings = Settings()
