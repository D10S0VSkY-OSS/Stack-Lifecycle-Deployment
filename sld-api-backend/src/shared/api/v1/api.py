from fastapi import APIRouter

from src.activityLogs.api.v1 import activity_logs
from src.aws.api.v1 import aws
from src.azure.api.v1 import azure
from src.custom_providers.api.v1 import custom_providers
from src.deploy.api.v1 import deploy, plan, schedule
from src.gcp.api.v1 import gcp
from src.healthy.api.v1 import healthy
from src.stacks.api.v1 import stacks
from src.tasks.api.v1 import tasks
from src.users.api.v1 import auth, users
from src.variables.api.v1 import variables

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(auth.router, prefix="/authenticate", tags=["AccessToken"])
api_router.include_router(aws.router, prefix="/accounts/aws", tags=["Aws"])
api_router.include_router(gcp.router, prefix="/accounts/gcp", tags=["Gcloud"])
api_router.include_router(
    custom_providers.router,
    prefix="/accounts/custom_providers",
    tags=["CustomProviders"],
)
api_router.include_router(azure.router, prefix="/accounts/azure", tags=["Azure"])
api_router.include_router(stacks.router, prefix="/stacks", tags=["Stacks"])
api_router.include_router(plan.router, prefix="/plan", tags=["Plan"])
api_router.include_router(deploy.router, prefix="/deploy", tags=["Deploy"])
api_router.include_router(schedule.router, prefix="/schedule", tags=["Schedule"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(activity_logs.router, prefix="/activity", tags=["Logs"])
api_router.include_router(variables.router, prefix="/variables", tags=["Variables"])
api_router.include_router(healthy.router, tags=["Healthy"])
