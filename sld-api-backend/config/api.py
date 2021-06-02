from typing import List
import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    #Schedle config
    SCHEDULE_SERVER: str = os.getenv('SLD_SCHEDULE_SERVER', "http://schedule:10000")
    # API server  config
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "API Stack Lifecycle Deployment"
    DESCRIPTION: str = '''
    OpenSource solution that defines and manages the complete lifecycle of resources used and provisioned into a cloud
                    '''
    VERSION: str = "1.0.0"
    AWS_PREFIX: List = ["aws", "amazon"]
    GCLOUD_PREFIX: List = ["gcloud", "gcp", "google"]
    AZURE_PREFIX: List = ["azure", "azurerm"]
    PROVIDERS_SUPPORT: List = AWS_PREFIX + GCLOUD_PREFIX + AZURE_PREFIX
    SECRET_KEY: str = os.getenv('SLD_SECRET_KEY', "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
    ALGORITHM = "HS256"
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    SECRET_VAULT: bytes = os.getenv('SLD_SECRET_VAULT', b'h0aW9hCz_wmEplvlFdoWjqx2pund1gGlcoZ2eqvYpCM=')
    PASSWORD_LEN: int = os.getenv('SLD_PASSWORD_LEN', 8)
    ROLLBACK: bool = os.getenv('SLD_ROLLBACK', False)
    DEPLOY_TMOUT: int =os.getenv('SLD_DEPLOY_TMOUT', 7200 ) 
    GIT_TMOUT: int =os.getenv('SLD_GIT_TMOUT',60 ) 
    WORKER_TMOUT: int =os.getenv('SLD_WORKER_TMOUT', 300 ) 
    ENV: str = os.getenv('SLD_ENV', "dev")
    DEBUG: bool = os.getenv('SLD_DEBUG', False)
    #init user
    INIT_USER = {
        "username": os.getenv('SLD_INIT_USER_NAME', "admin"),
        "fullname": os.getenv('SLD_INIT_USER_FULLNAME', "Master of the universe user"),
        "email": os.getenv('SLD_INIT_USER_email', "admin@example.com")
    }
    AWS_CONGIG_DEFAULT_FOLDER: str = f"{os.environ['HOME']}/.aws"
    AWS_SHARED_CREDENTIALS_FILE: str = f"{AWS_CONGIG_DEFAULT_FOLDER}/credentials"
    AWS_SHARED_CONFIG_FILE: str = f"{AWS_CONGIG_DEFAULT_FOLDER}/config"
    TASK_MAX_RETRY: int = os.getenv('SLD_TASK_MAX_RETRY', 1)
    TASK_RETRY_INTERVAL: int = os.getenv('SLD_TASK_RETRY_INTERVAL', 5)
    TERRAFORM_BIN_REPO: str = os.getenv('SLD_TERRAFORM_BIN_REPO', "https://releases.hashicorp.com/terraform")
    REMOTE_STATE: str = os.getenv('SLD_REMOTE_STATE', "http://remote-state:8080")


settings = Settings()
