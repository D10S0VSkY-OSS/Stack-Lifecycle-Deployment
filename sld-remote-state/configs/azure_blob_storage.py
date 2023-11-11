# https://docs.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-python?tabs=environment-variable-linux

import os

from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    CONTAINER: str = os.getenv("SLD_CONTAINER", "sld-remote-state")
    AZURE_STORAGE_CONNECTION_STRING: str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")


settings = Settings()
