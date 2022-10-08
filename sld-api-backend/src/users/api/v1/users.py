from config.api import settings
from src.activityLogs.infrastructure import repositories  as crud_activity
from src.users.infrastructure import repositories as crud_users
from fastapi import APIRouter, Depends, HTTPException
from helpers.get_data import (activity_log, check_role_user, check_squad_user,
                              user_squad_scope)
from src.users.domain.entities.users import (PasswordReset, User, UserCreate, UserInit,
                             UserUpdate)
from security import deps
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/start", response_model=User)
async def create_init_user(passwd: UserInit, db: Session = Depends(deps.get_db)):
    """
    Create init user
    """
    init_user = settings.INIT_USER
    deps.validate_password(init_user.get("username"), passwd.password)
    db_user = crud_users.get_user_by_username(db, username=init_user.get("username"))
    if db_user:
        raise HTTPException(status_code=409, detail="Username already registered")
    else:
        try:
            return crud_users.create_init_user(db=db, password=passwd.password)
        except Exception as err:
            raise HTTPException(status_code=400, detail=str(err))


@router.post("/", response_model=User)
async def create_user(
    user: UserCreate,
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):
    """
    Create user and define squad and privilege
    """

    # Check if the user has privileges
    if not crud_users.is_superuser(db, current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    # Check role
    roles = ["yoda", "darth_vader", "stormtrooper", "R2-D2"]
    if not all(item in roles for item in user.role):
        raise HTTPException(
            status_code=403,
            detail='Only supported roles "yoda", "darth_vader", "stormtrooper".If the user is a bot you can pass R2-D2 together to a role like this ["yoda", "R2-D2"]',
        )
    # Check if the user with squad * not have role yoda
    if "*" in user.squad and "yoda" not in user.role:
        raise HTTPException(
            status_code=403,
            detail="It is not possible to use * squad when role is not yoda",
        )
    # Get squad from current user
    if not crud_users.is_master(db, current_user):
        if not check_squad_user(current_user.squad, user.squad):
            raise HTTPException(
                status_code=403,
                detail=f"Not enough permissions for some of these squads {user.squad}",
            )
        if not check_role_user(current_user.role, user.role):
            raise HTTPException(
                status_code=403,
                detail=f"Not enough permissions for some of these roles {user.role}",
            )
    # Check if user exists
    db_user = crud_users.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    deps.validate_password(user.username, user.password)
    try:
        result = crud_users.create_user(db=db, user=user)
        db_task = crud_activity.create_activity_log(
            db=db,
            username=current_user.username,
            squad=user.squad,
            action=f"Create User {user.username}",
        )
        return result
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))


@router.patch("/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    user: UserUpdate,
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):
    """
    Update user
    """
    # Check if the user has privileges
    if not crud_users.is_superuser(db, current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    # Check role
    roles = ["yoda", "darth_vader", "stormtrooper", "R2-D2"]
    if not all(item in roles for item in user.role):
        raise HTTPException(
            status_code=403,
            detail='Only supported roles "yoda", "darth_vader", "stormtrooper".If the user is a bot you can pass R2-D2 together to a role like this ["yoda", "R2-D2"]',
        )
    # Check if the user with squad * not have role yoda
    if "*" in user.squad and "yoda" not in user.role:
        raise HTTPException(
            status_code=403,
            detail="It is not possible to use * squad when role is not yoda",
        )
    # Get squad from current user
    if not crud_users.is_master(db, current_user):
        current_squad = current_user.squad
        if not check_squad_user(current_squad, user.squad):
            raise HTTPException(
                status_code=403,
                detail=f"Not enough permissions for some of these squads {user.squad}",
            )
        if not check_role_user(current_user.role, user.role):
            raise HTTPException(
                status_code=403,
                detail=f"Not enough permissions for some of these roles {user.role}",
            )
    check_None = [None, "", "string"]
    if user.password not in check_None:
        deps.validate_password(user.username, user.password)
    try:
        # Push task data
        result = crud_users.update_user(db=db, user_id=user_id, user=user)
        db_task = crud_activity.create_activity_log(
            db=db,
            username=current_user.username,
            squad=user.squad,
            action=f"Update user {result.username}",
        )
        return result
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))


@router.patch("/reset/")
async def password_reset(
    passwd: PasswordReset,
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):
    """
    reset user
    """
    user_id = current_user.id
    deps.validate_password(current_user.username, passwd.passwd)
    try:
        result = crud_users.password_reset(db=db, user_id=user_id, password=passwd)
        db_task = crud_activity.create_activity_log(
            db=db,
            username=current_user.username,
            squad=current_user.squad,
            action=f"Reset password",
        )
        return {"result": "Password updated"}
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))


@router.get("/")
async def list_users(
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
):
    """
    List users
    """
    if not crud_users.is_superuser(db, current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    try:
        if not crud_users.is_master(db, current_user):
            return crud_users.get_users_by_squad(
                db=db, squad=current_user.squad, skip=skip, limit=limit
            )
        return crud_users.get_users(db=db, skip=skip, limit=limit)
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))


@router.get("/{user}")
async def list_user_by_id_or_name(
    user,
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):
    """
    List user by id or name
    """
    if crud_users.is_master(db, current_user):
        if not user.isdigit():
            return crud_users.get_user_by_username(db=db, username=user)
        return crud_users.get_user_by_id(db=db, id=user)

    if not crud_users.is_superuser(db, current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if not user_squad_scope(db, user, current_user.squad):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    try:
        if not user.isdigit():
            return crud_users.get_user_by_username(db=db, username=user)
        return crud_users.get_user_by_id(db=db, id=user)
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))


@router.delete("/{user}")
@activity_log
async def delete_user_by_id_or_username(
    user,
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):

    if crud_users.is_master(db, current_user):
        if not user.isdigit():
            return crud_users.delete_user_by_name(db=db, username=user)
        return crud_users.delete_user_by_id(db=db, id=user)
    if not crud_users.is_superuser(db, current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if not user_squad_scope(db, user, current_user.squad):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    try:
        if not user.isdigit():
            return crud_users.delete_user_by_name(db=db, username=user)
        result = crud_users.delete_user_by_id(db=db, id=user)
        return result
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))
