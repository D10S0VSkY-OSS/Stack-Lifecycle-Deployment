from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from src.activityLogs.infrastructure import repositories as crud_activity
from src.gcp.domain.entities import gcp as schemas_gcp
from src.gcp.infrastructure import repositories as crud_gcp
from src.shared.security import deps
from src.users.domain.entities import users as schemas_users
from src.users.infrastructure import repositories as crud_users
from src.shared.domain.exeptions.in_use import ResourceInUseError


async def update_gcp_account(
    gcp_account_id: int,
    gcp: schemas_gcp.GcloudAccountUpdate,
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> schemas_gcp.GcloudResponse:
    if not crud_users.is_master(db, current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    try:
        filters = schemas_gcp.GcloudAccountFilter()
        filters.id = gcp_account_id
        db_gcp_account = await crud_gcp.get_all_gcloud_profile(db=db, filters=filters)
        if not db_gcp_account:
            raise HTTPException(status_code=404, detail="Account not found")
        result = await crud_gcp.update_gcloud_profile(db=db, gcp_account_id=gcp_account_id, updated_gcp=gcp)
        crud_activity.create_activity_log(
            db=db,
            username=current_user.username,
            squad=current_user.squad,
            action=f"Update AWS account {gcp.squad} {gcp.environment}",
        )
        return result
    except ResourceInUseError as err:
        raise HTTPException(status_code=409, detail=str(err))
    except Exception as err:
        raise err
