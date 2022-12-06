from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from src.activityLogs.infrastructure import repositories as crud_activity
from src.custom_providers.infrastructure import repositories as crud_custom_provider
from src.shared.security import deps
from src.users.domain.entities import users as schemas_users
from src.users.infrastructure import repositories as crud_users


async def custom_provider_account_by_id(
    custom_provider_id,
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):
    if not crud_users.is_master(db, current_user):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    result = crud_custom_provider.delete_custom_profile_by_id(
        db=db, custom_profile_id=custom_provider_id
    )

    crud_activity.create_activity_log(
        db=db,
        username=current_user.username,
        squad=current_user.squad,
        action=f"Delete custom provider account {custom_provider_id} squad",
    )
    return result
