from fastapi import Depends, HTTPException, Response
from sqlalchemy.orm import Session

from src.activityLogs.infrastructure import repositories as crud_activity
from src.gcp.domain.entities import gcp as schemas_gcp
from src.gcp.infrastructure import repositories as crud_gcp
from src.shared.security import deps
from src.users.domain.entities import users as schemas_users
from src.users.infrastructure import repositories as crud_users


async def new_gcp_account(
    gcp: schemas_gcp.GcloudBase,
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):
    if not crud_users.is_master(db, current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if "string" in [gcp.squad, gcp.environment]:
        raise HTTPException(
            status_code=409,
            detail="The squad or environment field must have a value that is not a string.",
        )
    filters = schemas_gcp.GcloudAccountFilter()
    filters.squad = gcp.squad
    filters.environment = gcp.environment
    db_aws_account = await crud_gcp.get_all_gcloud_profile(
        db=db, filters=filters
    )
    if db_aws_account:
        raise HTTPException(status_code=409, detail="Account already exists")
    try:
        result = await crud_gcp.create_gcloud_profile(
            db=db,
            gcp=gcp,
        )
        crud_activity.create_activity_log(
            db=db,
            username=current_user.username,
            squad=current_user.squad,
            action=f"Create GCP account {gcp.squad} {gcp.environment}",
        )
        return result
    except Exception as err:
        raise HTTPException(status_code=400, detail=err)
