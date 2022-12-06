from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from src.activityLogs.infrastructure import repositories as crud_activity
from src.gcp.infrastructure import repositories as crud_gcp
from src.shared.security import deps
from src.users.domain.entities import users as schemas_users
from src.users.infrastructure import repositories as crud_users


async def gcloud_account_by_id(
    gcloud_account_id,
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):
    if not crud_users.is_master(db, current_user):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    result = crud_gcp.delete_gcloud_profile_by_id(
        db=db, gcloud_profile_id=gcloud_account_id
    )
    crud_activity.create_activity_log(
        db=db,
        username=current_user.username,
        squad=current_user.squad,
        action=f"Delete GCP account {gcloud_account_id} squad",
    )
    return result
