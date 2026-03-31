from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    OCR_MODEL_LANG: str = "es"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
