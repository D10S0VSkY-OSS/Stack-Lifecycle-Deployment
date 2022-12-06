from fastapi import Depends, HTTPException
from src.shared.security import deps
from sqlalchemy.orm import Session
from src.activityLogs.infrastructure import repositories as crud_activity
from src.azure.infrastructure import repositories as crud_azure
from src.users.domain.entities import users as schemas_users
from src.users.infrastructure import repositories as crud_users




async def azure_account_by_id(
    azure_account_id: int,
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):

    if not crud_users.is_master(db, current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    result = crud_azure.delete_azure_profile_by_id(
        db=db, azure_profile_id=azure_account_id
    )
    crud_activity.create_activity_log(
        db=db,
        username=current_user.username,
        squad=current_user.squad,
        action=f"Delete Azure account {azure_account_id}",
    )
    return result
