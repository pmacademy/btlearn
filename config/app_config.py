from typing import List
from pydantic import BaseSettings
from functools import lru_cache
import os
from pathlib import Path

config_dir = Path(__file__).resolve().parent

class Configurations(BaseSettings):
    DATABASE_URL: str
    GOOGLE_CLIENT_ID: str
    TOKEN_VALIDITY_DAYS: int = 0
    TOKEN_VALIDITY_HOURS: int = 0
    TOKEN_VALIDITY_MINUTES: int = 10
    PRIVATE_KEY: str
    PUBLIC_KEY: str
    ALLOWED_ORIGINS: List[str] = [
        "http://bytelearn-teacherdashboard-dev.s3-website.ap-south-1.amazonaws.com", "http://localhost", "http://localhost:3000"]
    ALLOWED_METHODS: List[str] = ["*"]
    ALLOWED_HEADERS: List[str] = ["*"]

    class Config:
        env_file = os.path.join(config_dir,'.env')


@lru_cache()
def get_config() -> Configurations:
    if(os.getenv("ENV", None) == "DEV"):
        return Configurations(_env_file=os.path.join(config_dir,'dev.env'))
    else:
        return Configurations(_env_file=os.path.join(config_dir,'.env'))