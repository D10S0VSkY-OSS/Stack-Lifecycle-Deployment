from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Response

from schemas import schemas
from crud import aws as crud_aws
from crud import user as crud_users
from crud import activityLogs as crud_activity
from security import deps


router = APIRouter()


@router.post("/", status_code=200)
async def create_new_aws_profile(
        aws: schemas.AwsAsumeProfile,
        response: Response,
        current_user: schemas.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)):

    if not current_user.master:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    try:
        result = crud_aws.create_aws_profile(db=db, aws=aws)
        crud_activity.create_activity_log(
            db=db,
            username=current_user.username,
            squad=current_user.squad,
            action=f'Create AWS account {aws.squad} {aws.environment}'
        )
        return result
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))


@router.get("/")
async def get_all_aws_accounts(
        current_user: schemas.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)):
    if not current_user.master:
        return crud_aws.get_squad_aws_profile(db=db, squad=current_user.squad)
    return crud_aws.get_all_aws_profile(db=db)


@router.delete("/{aws_account_id}")
async def delete_aws_account_by_id(
        aws_account_id: int,
        current_user: schemas.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)):

    if not current_user.master:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    result = crud_aws.delete_aws_profile_by_id(db=db, aws_profile_id=aws_account_id)
    crud_activity.create_activity_log(
        db=db,
        username=current_user.username,
        squad=current_user.squad,
        action=f'Delete AWS account {aws_account_id}'
    )
    return result
