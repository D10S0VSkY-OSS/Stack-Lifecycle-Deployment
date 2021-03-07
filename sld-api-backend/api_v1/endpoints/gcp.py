from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Response

from schemas import schemas
from crud import gcp as crud_gcp
from crud import user as crud_users
from crud import activityLogs as crud_activity
from security import deps


router = APIRouter()


@router.post("/", status_code=200)
async def create_new_gcloud_profile(
        gcp: schemas.GcloudBase,
        response: Response,
        current_user: schemas.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)):
    if not current_user.master:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    try:
        result = crud_gcp.create_gcloud_profile(
            db=db,
            squad=gcp.squad,
            environment=gcp.environment,
            gcloud_keyfile_json=gcp.gcloud_keyfile_json)
        crud_activity.create_activity_log(
            db=db,
            username=current_user.username,
            squad=current_user.squad,
            action=f'Create GCP account {result.id}'
        )
        return result
    except Exception as err:
        raise HTTPException(status_code=400, detail=err)


@router.get("/")
async def get_all_gcloud_accounts(
        current_user: schemas.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)):
    if not current_user.master:
        return crud_gcp.get_squad_gcloud_profile(db=db, squad=current_user.squad)
    return crud_gcp.get_all_gcloud_profile(db=db)


@router.delete("/{gcloud_account_id}")
async def delete_gcloud_account_by_id(
        gcloud_account_id,
        current_user: schemas.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)):
    if not current_user.master:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    result = crud_gcp.delete_gcloud_profile_by_id(
        db=db, gcloud_profile_id=gcloud_account_id)
    crud_activity.create_activity_log(
        db=db,
        username=current_user.username,
        squad=current_user.squad,
        action=f'Delete GCP account {gcloud_account_id} squad'
    )
    return result
