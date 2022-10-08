from src.activityLogs.crud import activityLogs as crud_activity
from src.gcp.crud import gcp as crud_gcp
from src.gcp.schema import gcp as schemas_gcp
from src.users.crud import user as crud_users
from src.users.schema import users as schemas_users
from fastapi import APIRouter, Depends, HTTPException, Response
from security import deps
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/", status_code=200)
async def create_new_gcloud_profile(
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


@router.get("/")
async def get_all_gcloud_accounts(
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):
    if not crud_users.is_master(db, current_user):
        return crud_gcp.get_squad_gcloud_profile(
            db=db, squad=current_user.squad, environment=None
        )
    return crud_gcp.get_all_gcloud_profile(db=db)


@router.delete("/{gcloud_account_id}")
async def delete_gcloud_account_by_id(
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
