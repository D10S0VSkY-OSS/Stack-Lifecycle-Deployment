from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from crud import user as crud_users
from crud import activityLogs as crud_activity
from helpers.get_data import userSquadScope, activity_log
from security import deps
from schemas.schemas import (
    User, UserCreate, UserUpdate, PasswordReset)


router = APIRouter()


@router.post("/", response_model=User)
async def create_user(
    user: UserCreate, current_user: User = Depends(
        deps.get_current_active_user), db: Session = Depends(
            deps.get_db)):
    '''
    Create user and define squad and privilege
    '''
    db_user = crud_users.get_user_by_username(db, username=user.username)
    if not crud_users.is_superuser(db, current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered")
    deps.validate_password(user.password)
    try:
        result = crud_users.create_user(
            db=db, squad=current_user.squad, user=user)
        db_task = crud_activity.create_activity_log(
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
        user_id: str,
        user: UserUpdate,
        current_user: User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)):
    '''
    Update user
    '''
    if not crud_users.is_superuser(db, current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if not userSquadScope(db, user_id, current_user.squad):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    check_None = [None, "", "string"]
    if user.password not in check_None:
        deps.validate_password(user.password)
    try:
        # Push task data
        result = crud_users.update_user(db=db, user_id=user_id, user=user)
        db_task = crud_activity.create_activity_log(
            db=db,
            username=current_user.username,
            squad=current_user.squad,
            action=f'Update user {current_user.username}'
        )
        return result
    except Exception as err:
        raise HTTPException(
            status_code=400,
            detail=str(err))


@router.patch("/reset/")
async def password_reset(
        passwd: PasswordReset,
        current_user: User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)):
    '''
    reset user
    '''
    user_id = current_user.id
    deps.validate_password(passwd.passwd)
    try:
        result = crud_users.password_reset(
            db=db, user_id=user_id, password=passwd)
        db_task = crud_activity.create_activity_log(
            db=db,
            username=current_user.username,
            squad=current_user.squad,
            action=f'Reset password'
        )
        return result
    except Exception as err:
        raise HTTPException(
            status_code=400,
            detail=str(err))


@router.get("/")
async def list_users(
        current_user: User = Depends(deps.get_current_active_user),
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(deps.get_db)):
    '''
    List users
    '''
    if not crud_users.is_superuser(db, current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    try:
        if current_user.master:
            return crud_users.get_users(db=db, skip=skip, limit=limit)
        else:
            return crud_users.get_users_by_squad(db=db, squad=current_user.squad, skip=skip, limit=limit)
    except Exception as err:
        raise HTTPException(
            status_code=400,
            detail=str(err))


@router.get("/{user}")
async def list_user_by_id_or_name(
        user,
        current_user: User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)):
    '''
    List user by id or name
    '''
    if current_user.master:
        if not user.isdigit():
            return crud_users.get_user_by_username(db=db, username=user)
        return crud_users.get_user_by_id(db=db, id=user)

    if not crud_users.is_superuser(db, current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if not userSquadScope(db, user, current_user.squad):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    try:
        if not user.isdigit():
            return crud_users.get_user_by_username(db=db, username=user)
        return crud_users.get_user_by_id(db=db, id=user)
    except Exception as err:
        raise HTTPException(
            status_code=400,
            detail=str(err))


@router.delete("/{user}")
@activity_log
async def delete_user_by_id_or_username(
        user,
        current_user: User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)):

    if current_user.master:
        if not user.isdigit():
            return crud_users.delete_user_by_name(db=db, username=user)
        return crud_users.delete_user_by_id(db=db, id=user)
    if not crud_users.is_superuser(db, current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if not userSquadScope(db, user, current_user.squad):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    try:
        if not user.isdigit():
            return crud_users.delete_user_by_name(db=db, username=user)
        result = crud_users.delete_user_by_id(db=db, id=user)
        return result
    except Exception as err:
        raise HTTPException(
            status_code=400,
            detail=str(err))
