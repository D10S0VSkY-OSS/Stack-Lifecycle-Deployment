from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from src.activityLogs.infrastructure import repositories as crud_activity
from src.shared.helpers.get_data import check_role_user, check_squad_user
from src.shared.security import deps
from src.users.domain.entities.users import PasswordReset, User, UserUpdate
from src.users.infrastructure import repositories as crud_users


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
