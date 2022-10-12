import imp
import logging
from pkgutil import ImpImporter
from statistics import mode

from src.shared.api.v1.api import api_router
from config.api import settings
from config.database import engine
from fastapi import FastAPI
from src.activityLogs.infrastructure import models as model_activity
from src.aws.infrastructure import models as model_aws
from src.azure.infrastructure import models as model_azure
from src.deploy.infrastructure import models as model_deploy
from src.gcp.infrastructure import models as model_gcp
from src.stacks.infrastructure import models as model_stacks
from src.tasks.infrastructure import models as model_tasks
from src.custom_providers.infrastructure import models as model_custom_provider
# from db import models
## Need refactor
from src.users.infrastructure import models as model_users

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# Need refactor
model_users.Base.metadata.create_all(bind=engine)
model_activity.Base.metadata.create_all(bind=engine)
model_stacks.Base.metadata.create_all(bind=engine)
model_deploy.Base.metadata.create_all(bind=engine)
model_tasks.Base.metadata.create_all(bind=engine)
model_aws.Base.metadata.create_all(bind=engine)
model_azure.Base.metadata.create_all(bind=engine)
model_gcp.Base.metadata.create_all(bind=engine)
model_custom_provider.Base.metadata.create_all(bind=engine)


app = FastAPI(
    title=f"{settings.PROJECT_NAME}",
    description=f"{settings.DESCRIPTION}",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    version=f"{settings.VERSION}",
)

app.include_router(api_router, prefix=settings.API_V1_STR)
