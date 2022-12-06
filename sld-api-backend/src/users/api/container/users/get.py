from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from src.shared.helpers.get_data import user_squad_scope
from src.shared.security import deps
from src.users.domain.entities.users import User
from src.users.infrastructure import repositories as crud_users


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
