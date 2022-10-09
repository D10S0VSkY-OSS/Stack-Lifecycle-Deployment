from src.aws.api.v1 import aws
from src.azure.api.v1 import azure
from src.gcp.api.v1 import gcp
from src.activityLogs.api.v1 import activity_logs
from src.deploy.api.v1 import deploy, schedule, plan
from src.stacks.api.v1 import stacks
from src.tasks.api.v1 import tasks
from src.users.api.v1 import users, auth
from src.variables.api.v1 import variables
from src.healthy.api.v1 import healthy
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(auth.router, prefix="/authenticate", tags=["AccessToken"])
api_router.include_router(aws.router, prefix="/accounts/aws", tags=["Aws"])
api_router.include_router(gcp.router, prefix="/accounts/gcp", tags=["Gcloud"])
api_router.include_router(azure.router, prefix="/accounts/azure", tags=["Azure"])
api_router.include_router(stacks.router, prefix="/stacks", tags=["Stacks"])
api_router.include_router(plan.router, prefix="/plan", tags=["Plan"])
api_router.include_router(deploy.router, prefix="/deploy", tags=["Deploy"])
api_router.include_router(schedule.router, prefix="/schedule", tags=["Schedule"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(activity_logs.router, prefix="/activity", tags=["Logs"])
api_router.include_router(variables.router, prefix="/variables", tags=["Variables"])
api_router.include_router(healthy.router, tags=["Healthy"])
