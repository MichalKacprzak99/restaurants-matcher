from functools import lru_cache
from typing import List

from pydantic import BaseSettings


class Settings(BaseSettings):
    URI: str = ''
    DB_USER: str = ''
    DB_PASSWORD: str = ''
    API_PREFIX: str = "/api_v1"
    ALLOWED_HOSTS: List[str] = ['*']
    PROJECT_NAME: str = "Student project"

    class Config:
        env_file = "app/core/.env"
        env_file_encoding = 'utf-8'


@lru_cache()
def get_settings():
    return Settings()
