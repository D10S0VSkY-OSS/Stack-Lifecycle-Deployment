from fastapi import APIRouter, Depends

from src.activityLogs.api.container import get
from src.users.domain.entities import users as schemas_users

router = APIRouter()


@router.get("/id/{username}")
async def get_activity_logs_by_username(
    get_activity: schemas_users.User = Depends(get.get_activity_logs_by_username),
):
    return get_activity


@router.get("/all")
async def get_all_activity_logs(
    get_all_activity: schemas_users.User = Depends(get.get_all_activity_logs),
):
    return get_all_activity
