import ast
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from celery.result import AsyncResult
from celery.task.control import revoke

from schemas import schemas
from security import deps
from crud import tasks as crud_tasks

#from fastapi_limiter import FastAPILimiter
#from fastapi_limiter.depends import RateLimiter
#import aioredis

router = APIRouter()

#@router.on_event("startup")
#async def startup():
#    redis = await aioredis.create_redis_pool("redis://redis:6379")
#    FastAPILimiter.init(redis)


@router.delete("/id/{task_id}")
async def get_task_by_id(
        task_id: str,
        current_user: schemas.User = Depends(deps.get_current_active_user)):
        result = revoke(task_id, terminate=True)
        return {"result": f'REVOKE {task_id}'}

@router.get("/id/{task_id}")
async def get_task_by_id(
        task_id: str,
        current_user: schemas.User = Depends(deps.get_current_active_user)):
    a = AsyncResult(task_id)
    cstr = str(a.info)
    try:
        parse = ast.literal_eval(cstr)
    except Exception as err:
        parse = str(cstr)
    result = {
        "result": {
            "state": a.state, "module": parse, "status": a.status}}
    return result


@ router.get("/all")
async def get_all_tasks(
        current_user: schemas.User = Depends(deps.get_current_active_user),
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(deps.get_db)):
    try:
        if current_user.master:
            result = crud_tasks.get_all_tasks(db=db, skip=skip, limit=limit)
            return result
        else:
            squad = current_user.squad
            result = crud_tasks.get_all_tasks_by_squad(db=db, squad=squad, skip=skip, limit=limit)
            return result
    except Exception as err:
        raise HTTPException(
            status_code=400,
            detail=f"{err}")


@ router.get("/deploy_id/{id}")
async def get_task_by_deploy_id(
        id: int,
        current_user: schemas.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)):
    try:
        squad = current_user.squad
        result = crud_tasks.get_tasks_by_deploy_id(db=db, deploy_id=id, squad=squad)
        return result
    except Exception as err:
        raise HTTPException(
            status_code=400,
            detail=f"{err}")
