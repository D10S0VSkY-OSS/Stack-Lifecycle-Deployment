import logging

from api_v1.api import api_router
from config.api import settings
from config.database import engine
from db import models
from fastapi import FastAPI

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=f"{settings.PROJECT_NAME}",
    description=f"{settings.DESCRIPTION}",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    version=f"{settings.VERSION}",
)

app.include_router(api_router, prefix=settings.API_V1_STR)
