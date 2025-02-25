import os
from logging import config as logging_config

from core.logger import LOGGING
from pydantic_settings import BaseSettings, SettingsConfigDict

logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )
    PROJECT_NAME: str = "project"
    APP_RELOAD: bool = False
    
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


settings = Settings()
