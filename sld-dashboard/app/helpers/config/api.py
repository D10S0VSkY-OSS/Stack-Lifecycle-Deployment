import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SERVER: str = os.getenv("SLD_API_SERVER", "http://api-backend")
    PORT: str = os.getenv("SLD_API_SERVER_PORT", "8000")
    API: str = os.getenv("SLD_API_VER", "/api/v1")
    EXTERNAL_DNS_API: str = os.getenv(
        "SLD_EXTERNAL_DNS_API", "http://api-backend:8000/docs"
    )
    SCHEDULE: str = os.getenv("SLD_SCHEDULE_SERVER", "http://schedule:10000")
    REMOTE_STATE: str = os.getenv("SLD_REMOTE_STATE", "http://remote-state:8080")
    SECRET_VAULT: bytes = os.getenv(
        "SLD_SECRET_VAULT", b"h0aW9hCz_wmEplvlFdoWjqx2pund1gGlcoZ2eqvYpCM="
    )
    SORT_BY_DESC: bool = os.getenv("SLD_SORT", False)


settings = Settings()
