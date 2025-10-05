from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from src.activityLogs.infrastructure import repositories as crud_activity
from src.gcp.infrastructure import repositories as crud_gcp
from src.gcp.domain.entities import gcp as schemas_gcp
from src.shared.security import deps
from src.users.domain.entities import users as schemas_users
from src.users.infrastructure import repositories as crud_users
from src.shared.domain.exeptions.in_use import ResourceInUseError


async def gcp_account_by_id(
    gcp_account_id: int,
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> schemas_gcp.GcloudResponse:
    if not crud_users.is_master(db, current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    filters = schemas_gcp.GcloudAccountFilter()
    filters.id = gcp_account_id
    db_gcp_account = await crud_gcp.get_all_gcloud_profile(db=db, filters=filters)
    if not db_gcp_account:
        raise HTTPException(status_code=404, detail="Account not found")
    try:
        result = await crud_gcp.delete_gcloud_profile_by_id(db=db, gcp_account_id=gcp_account_id)
        crud_activity.create_activity_log(
            db=db,
            username=current_user.username,
            squad=current_user.squad,
            action=f"Delete AWS account {gcp_account_id}",
        )
        return result
    except ResourceInUseError as err:
        raise HTTPException(status_code=409, detail=str(err))
    except Exception as err:
        raise err
