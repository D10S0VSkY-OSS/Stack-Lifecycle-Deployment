from config.celery_config import celery_app
from fastapi import Depends

from src.shared.security import deps
from src.users.domain.entities import users as schemas_users


async def get_task_by_id(
    task_id: str,
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
):
    result = celery_app.control.revoke(task_id, terminate=True)
    return {"result": f"REVOKE {task_id}"}
