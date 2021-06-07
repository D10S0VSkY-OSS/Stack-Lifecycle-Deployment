from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from crud import master as crud_master
from crud import activityLogs as crud_activity
from security import deps
from config.api import settings
from schemas.schemas import (
    User, UserCreateMaster, UserInit)


router = APIRouter()


@router.post("/start", response_model=User)
async def create_init_user(passwd: UserInit, db: Session = Depends(deps.get_db)):
    '''
    Create init user
    '''
    deps.validate_password(passwd.password)
    init_user = settings.INIT_USER
    db_user = crud_master.get_user_by_username(
        db, username=init_user.get("username"))
    if db_user:
        raise HTTPException(
            status_code=409,
            detail="Username already registered")
    else:
        try:
            return crud_master.create_init_user(db=db, password=passwd.password)
        except Exception as err:
            raise HTTPException(
                status_code=400,
                detail=str(err))
