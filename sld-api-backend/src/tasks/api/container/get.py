import ast

from celery.result import AsyncResult
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from src.shared.security import deps
from src.tasks.infrastructure import repositories as crud_tasks
from src.users.domain.entities import users as schemas_users
from src.users.infrastructure import repositories as crud_users


async def get_task_by_id(
    task_id: str,
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
):
    a = AsyncResult(task_id)
    cstr = str(a.info)
    try:
        parse = ast.literal_eval(cstr)
    except Exception:
        parse = str(cstr)
    result = {"result": {"state": a.state, "module": parse, "status": a.status}}
    return result


async def get_all_tasks(
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
):
    try:
        if not crud_users.is_master(db, current_user):
            squad = current_user.squad
            result = crud_tasks.get_all_tasks_by_squad(
                db=db, squad=squad, skip=skip, limit=limit
            )
            return result
        result = crud_tasks.get_all_tasks(db=db, skip=skip, limit=limit)
        return result
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"{err}")


async def get_task_by_deploy_id(
    id: int,
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):
    try:
        result = crud_tasks.get_tasks_by_deploy_id(db=db, deploy_id=id)
        return result
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"{err}")
