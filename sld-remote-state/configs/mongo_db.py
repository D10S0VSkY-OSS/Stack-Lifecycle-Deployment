import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGODB_URL: str = os.getenv("SLD_MONGODB_URL", "mongodb:27017/")
    MONGODB_DB_NAME: str = os.getenv("SLD_MONGODB_DB_NAME", "remote-state")
    MONGODB_USER: str = os.getenv("SLD_MONGODB_USER", "admin")
    MONGODB_PASSWD: str = os.getenv("SLD_MONGODB_PASSWD", "admin")


settings = Settings()
