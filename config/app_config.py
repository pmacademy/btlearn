from typing import List
from pydantic import BaseSettings
from functools import lru_cache
import os
from pathlib import Path

config_dir = Path(__file__).resolve().parent


class Configurations(BaseSettings):
    DATABASE_URL: str
    POOL_RECYCLE_TIME: int = 1800
    PUBLIC_KEY: str
    ALLOWED_ORIGINS: List[str] = ["*"]
    ALLOWED_METHODS: List[str] = ["*"]
    ALLOWED_HEADERS: List[str] = ["*"]
    REGION: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    TEACHER_DASHBOARD_URL: str
    QUESTIONS_DASHBOARD_URL: str
    AUTH_URL: str
    REPORTING_SERVICE_URL: str
    STUDENT_SIGN_IN_URL: str
    TEACHER_TOOL_CLIENT_ID: str
    TEACHER_TOOL_CLIENT_PASSWORD: str

    class Config:
        env_file = os.path.join(config_dir, '.env')


@lru_cache()
def get_config() -> Configurations:
    if(os.getenv("ENV", None) == "DEV"):
        return Configurations(_env_file=os.path.join(config_dir, '.env.dev'))
    elif(os.getenv("ENV", None) == "STG"):
        return Configurations(_env_file=os.path.join(config_dir, '.env.stg'))
    elif(os.getenv("ENV", None) == "PROD"):     
        return Configurations(_env_file=os.path.join(config_dir, '.env.prod'))    
    else:
        return Configurations(_env_file=os.path.join(config_dir, '.env'))
