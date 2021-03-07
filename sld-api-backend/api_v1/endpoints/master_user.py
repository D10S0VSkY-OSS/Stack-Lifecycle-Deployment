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


@router.post("/", response_model=User)
async def create_user(
    user: UserCreateMaster, current_user: User = Depends(
        deps.get_current_active_user), db: Session = Depends(
            deps.get_db)):
    '''
    Create user and define squad and privilege
    '''
    db_user = crud_master.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered")
    if not crud_master.is_master(db, current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    deps.validate_password(user.password)
    try:
        result = crud_master.create_user(db=db, user=user)
        crud_activity.create_activity_log(
            db=db,
            username=current_user.username,
            squad=current_user.squad,
            action=f'Create User {user.username}'
        )
        return result
    except Exception as err:
        raise HTTPException(
            status_code=400,
            detail=str(err))


@router.patch("/{user_id}", response_model=User)
async def update_user(
        user_id,
        user: UserCreateMaster,
        current_user: User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)):
    '''
    Update user
    '''
    if not crud_master.is_master(db, current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    check_None = [None, "", "string"]
    if user.password not in check_None:
        deps.validate_password(user.password)
    try:
        result = crud_master.update_user(db=db, user_id=user_id, user=user)
        crud_activity.create_activity_log(
            db=db,
            username=current_user.username,
            squad=current_user.squad,
            action=f'Update User {user.username}'
        )
        return result
    except Exception as err:
        raise HTTPException(
            status_code=400,
            detail=str(err))
