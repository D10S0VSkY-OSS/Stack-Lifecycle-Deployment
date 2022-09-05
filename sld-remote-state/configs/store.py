from typing import List
import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    SLD_STORE: str = os.getenv('SLD_STORE', "local")
    SLD_RM_VER: str = os.getenv('SLD_RM_VER', "2.4.0")

settings = Settings()
