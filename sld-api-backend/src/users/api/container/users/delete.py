from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from src.shared.helpers.get_data import activity_log, user_squad_scope
from src.shared.security import deps
from src.users.domain.entities.users import User
from src.users.infrastructure import repositories as crud_users


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
