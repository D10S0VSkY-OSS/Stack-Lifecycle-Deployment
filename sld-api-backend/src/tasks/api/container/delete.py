from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException

from src.shared.security import deps
from src.users.domain.entities import users as schemas_users
from src.tasks.infrastructure.repositories import delete_celery_task_meta_by_task_id


async def get_task_by_id(
    task_id: str,
    db: Session = Depends(deps.get_db),
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
):
    try:
        delete_celery_task_meta_by_task_id(db=db, task_id=task_id)
        return {"result": f"REVOKE {task_id}"}
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))
