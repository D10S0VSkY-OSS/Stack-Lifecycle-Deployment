import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BUCKET: str = os.getenv("SLD_BUCKET", "sld-remote-state")
    REGION: str = os.getenv("AWS_DEFAULT_REGION", "eu-west-1")
    AWS_ACCESS_KEY: str = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY")


settings = Settings()
