from config.api import settings
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from src.activityLogs.infrastructure import repositories as crud_activity
from src.shared.helpers.get_data import check_role_user, check_squad_user
from src.shared.security import deps
from src.users.domain.entities.users import User, UserCreate, UserInit
from src.users.infrastructure import repositories as crud_users


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
