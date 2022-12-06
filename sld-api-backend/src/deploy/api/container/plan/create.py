from fastapi import APIRouter, Depends, HTTPException, Response
from src.shared.security import deps
from sqlalchemy.orm import Session
from src.activityLogs.infrastructure import repositories as crud_activity
from src.gcp.domain.entities import gcp as schemas_gcp
from src.gcp.infrastructure import repositories as crud_gcp
from src.users.domain.entities import users as schemas_users
from src.users.infrastructure import repositories as crud_users
from src.deploy.infrastructure import repositories as crud_deploy

async def new_gcloud_profile(
    gcp: schemas_gcp.GcloudBase,
    response: Response,
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
    db_gcp_account = crud_gcp.get_squad_gcloud_profile(
        db=db, squad=gcp.squad, environment=gcp.environment
    )
    if db_gcp_account:
        raise HTTPException(status_code=409, detail="Account already exists")
    try:
        result = crud_gcp.create_gcloud_profile(
            db=db,
            squad=gcp.squad,
            environment=gcp.environment,
            gcloud_keyfile_json=gcp.gcloud_keyfile_json,
        )
        crud_activity.create_activity_log(
            db=db,
            username=current_user.username,
            squad=current_user.squad,
            action=f"Create GCP account {result.id}",
        )
        return {"result": f"Create GCP account {gcp.squad} {gcp.environment}"}
    except Exception as err:
        raise HTTPException(status_code=400, detail=err)

