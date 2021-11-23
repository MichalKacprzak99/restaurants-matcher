import os
from functools import lru_cache
from typing import List

from pydantic import BaseSettings


class Configuration(BaseSettings):
    URI: str
    DB_USER: str
    DB_PASSWORD: str
    API_PREFIX: str = "/api_v1"
    ALLOWED_HOSTS: List[str] = ['*']
    PROJECT_NAME: str = "Student project"


@lru_cache()
def get_configuration():
    return Configuration()
