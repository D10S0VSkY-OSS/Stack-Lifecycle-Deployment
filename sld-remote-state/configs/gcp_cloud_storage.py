# https://cloud.google.com/storage/docs/reference/libraries#create-service-account-console

import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BUCKET: str = os.getenv("SLD_BUCKET", "sld-remote-state")
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")


settings = Settings()
