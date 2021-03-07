import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    SERVER: str = os.getenv('SLD_API_SERVER', 'http://api-backend')
    PORT: str = os.getenv('SLD_API_SERVER_PORT', '8000')
    API: str = os.getenv('SLD_API_SERVER_API', '/api/v1')
    BOT: str = os.getenv('SLD_API_SERVER_USER', 'schedule')
    BOTC: str = os.getenv('SLD_API_SERVER_PASSWORD', 'Schedule1@local')
    CREDENTIALS_BOT: dict = {
        "username": BOT,
        "password": BOTC
    }
    LOG: dict = {
        "logger": {
            "level": "info",
            "rotation": "20 days",
            "retention": "1 months",
            "format": "<level>{level: <8}</level> <green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> request id: {extra[request_id]} - <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"

        }
    }


settings = Settings()
