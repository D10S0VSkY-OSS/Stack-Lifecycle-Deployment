import os
from typing import List

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Schedle config
    SCHEDULE_SERVER: str = os.getenv("SLD_SCHEDULE_SERVER", "http://schedule:10000")
    # API server  config
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "API Stack Lifecycle Deployment"
    DESCRIPTION: str = """
    OpenSource solution that defines and manages the complete lifecycle of resources used and provisioned into a cloud
                    """
    VERSION: str = "1.0.0"
    AWS_PREFIX: List = ["aws"]
    GCLOUD_PREFIX: List = ["gcp"]
    AZURE_PREFIX: List = ["azure"]
    CUSTOM_PREFIX: List = ["custom"]
    PROVIDERS_SUPPORT: List = AWS_PREFIX + GCLOUD_PREFIX + AZURE_PREFIX + CUSTOM_PREFIX
    SECRET_KEY: str = os.getenv(
        "SLD_SECRET_KEY",
        "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7",
    )
    ALGORITHM: str = "HS256"
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    SECRET_VAULT: bytes = os.getenv(
        "SLD_SECRET_VAULT", b"h0aW9hCz_wmEplvlFdoWjqx2pund1gGlcoZ2eqvYpCM="
    )
    PASSWORD_LEN: int = os.getenv("SLD_PASSWORD_LEN", 8)
    ROLLBACK: bool = os.getenv("SLD_ROLLBACK", False)
    DEPLOY_TMOUT: int = os.getenv("SLD_DEPLOY_TMOUT", 7200)
    GIT_TMOUT: int = os.getenv("SLD_GIT_TMOUT", 60)
    WORKER_TMOUT: int = os.getenv("SLD_WORKER_TMOUT", 300)
    ENV: str = os.getenv("SLD_ENV", "dev")
    DEBUG: bool = os.getenv("SLD_DEBUG", False)
    BACKEND_USER: str = os.getenv("BACKEND_USER", "")
    BACKEND_PASSWD: str = os.getenv("BACKEND_PASSWD", "")
    BACKEND_SERVER: str = os.getenv("BACKEND_SERVER", "redis")
    CACHE_USER: str = os.getenv("SLD_CACHE_USER", "")
    CACHE_PASSWD: str = os.getenv("SLD_CACHE_PASSWD", "")
    CACHE_SERVER: str = os.getenv("SLD_CACHE_SERVER", "redis")
    # init user
    INIT_USER: dict = {
        "username": os.getenv("SLD_INIT_USER_NAME", "admin"),
        "fullname": os.getenv("SLD_INIT_USER_FULLNAME", "Master of the universe user"),
        "email": os.getenv("SLD_INIT_USER_email", "admin@example.com"),
    }
    AWS_CONGIG_DEFAULT_FOLDER: str = f"{os.environ['HOME']}/.aws"
    AWS_SHARED_CREDENTIALS_FILE: str = f"{AWS_CONGIG_DEFAULT_FOLDER}/credentials"
    AWS_SHARED_CONFIG_FILE: str = f"{AWS_CONGIG_DEFAULT_FOLDER}/config"
    TASK_MAX_RETRY: int = os.getenv("SLD_TASK_MAX_RETRY", 0)
    TASK_RETRY_INTERVAL: int = os.getenv("SLD_TASK_RETRY_INTERVAL", 20)
    TASK_LOCKED_EXPIRED: int = os.getenv("SLD_TASK_LOCKED_EXPIRED", 300)
    TASK_ROUTE: bool = os.getenv("SLD_TASK_ROUTE", False)
    TERRAFORM_BIN_REPO: str = os.getenv(
        "SLD_TERRAFORM_BIN_REPO", "https://releases.hashicorp.com/terraform"
    )
    REMOTE_STATE: str = os.getenv("SLD_REMOTE_STATE", "http://remote-state:8080")
    BOT: str = os.getenv("SLD_API_SERVER_USER", "schedule")
    BOTC: str = os.getenv("SLD_API_SERVER_PASSWORD", "Schedule1@local")


settings = Settings()
