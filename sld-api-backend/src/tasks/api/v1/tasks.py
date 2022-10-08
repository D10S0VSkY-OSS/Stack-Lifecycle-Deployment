import ast

from celery.result import AsyncResult
from config.celery_config import celery_app
from src.tasks.crud import tasks as crud_tasks
from src.users.crud import user as crud_users
from src.users.schema import users as schemas_users
from fastapi import APIRouter, Depends, HTTPException
from security import deps
from sqlalchemy.orm import Session

router = APIRouter()


@router.delete("/id/{task_id}")
async def get_task_by_id(
    task_id: str, current_user: schemas_users.User = Depends(deps.get_current_active_user)
):
    result = celery_app.control.revoke(task_id, terminate=True)
    return {"result": f"REVOKE {task_id}"}


@router.get("/id/{task_id}")
async def get_task_by_id(
    task_id: str, current_user: schemas_users.User = Depends(deps.get_current_active_user)
):
    a = AsyncResult(task_id)
    cstr = str(a.info)
    try:
        parse = ast.literal_eval(cstr)
    except Exception:
        parse = str(cstr)
    result = {"result": {"state": a.state, "module": parse, "status": a.status}}
    return result


@router.get("/all")
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


@router.get("/deploy_id/{id}")
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
