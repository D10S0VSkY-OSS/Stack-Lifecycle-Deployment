from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Response

from schemas import schemas
from crud import fe as crud_fe
from crud import user as crud_users
from crud import activityLogs as crud_activity
from security import deps


router = APIRouter()


@router.post("/", status_code=200)
async def create_new_fe_profile(
        fe: schemas.feAsumeProfile,
        response: Response,
        current_user: schemas.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)):
    # Check if the user has privileges
    if not crud_users.is_master(db, current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if "string" in [fe.squad, fe.environment]:
        raise HTTPException(
            status_code=409,
            detail="The squad or environment field must have a value that is not a string.")
    db_fe_account = crud_fe.get_squad_fe_profile(
        db=db, squad=fe.squad, environment=fe.environment)
    if db_fe_account:
        raise HTTPException(
            status_code=409,
            detail="Account already exists")
    try:
        result = crud_fe.create_fe_profile(db=db, fe=fe)
        crud_activity.create_activity_log(
            db=db,
            username=current_user.username,
            squad=current_user.squad,
            action=f'Create FE account {fe.squad} {fe.environment}'
        )
        return {"result": f'Create FE account {fe.squad} {fe.environment}'}
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))


@router.get("/")
async def get_all_fe_accounts(
        current_user: schemas.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)):
    # Check if the user has privileges
    if not crud_users.is_master(db, current_user):
        return crud_fe.get_squad_fe_profile(db=db, squad=current_user.squad, environment=None )
    return crud_fe.get_all_fe_profile(db=db)


@router.delete("/{fe_account_id}")
async def delete_fe_account_by_id(
        fe_account_id: int,
        current_user: schemas.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)):

    if not crud_users.is_master(db, current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    result = crud_fe.delete_fe_profile_by_id(
        db=db, fe_profile_id=fe_account_id)
    crud_activity.create_activity_log(
        db=db,
        username=current_user.username,
        squad=current_user.squad,
        action=f'Delete FE account {fe_account_id}'
    )
    return result
