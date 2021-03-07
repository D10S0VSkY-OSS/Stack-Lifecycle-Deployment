from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException

from schemas import schemas
from security import deps
from crud import activityLogs as crud_activity

#from fastapi_limiter import FastAPILimiter
#from fastapi_limiter.depends import RateLimiter
#import aioredis

router = APIRouter()

# @router.on_event("startup")
# async def startup():
#    redis = await aioredis.create_redis_pool("redis://redis:6379")
#    FastAPILimiter.init(redis)


@router.get("/id/{username}")
async def get_activity_logs_by_username(
        username: str,
        current_user: schemas.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)):
    if not current_user.privilege:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if not current_user.master:
        squad = current_user.squad
        return crud_activity.get_activity_by_username_squad(db=db, username=username, squad=squad)
    return crud_activity.get_activity_by_username(db, username=username)


@ router.get("/all")
async def get_all_activity_logs(
        current_user: schemas.User = Depends(deps.get_current_active_user),
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(deps.get_db)):
    if not current_user.privilege:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    try:
        if not current_user.master:
            squad = current_user.squad
            result = crud_activity.get_all_activity_by_squad(
                db=db, squad=squad, skip=skip, limit=limit)
            return result
        result = crud_activity.get_all_activity(db=db, skip=skip, limit=limit)
        return result
    except Exception as err:
        raise HTTPException(
            status_code=400,
            detail=f"{err}")
