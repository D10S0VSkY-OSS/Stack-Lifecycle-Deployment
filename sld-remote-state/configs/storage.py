import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SLD_STORAGE_BACKEND: str = os.getenv("SLD_STORAGE_BACKEND", "local")
    SLD_RM_VER: str = os.getenv("SLD_RM_VER", "2.7.0")


settings = Settings()
