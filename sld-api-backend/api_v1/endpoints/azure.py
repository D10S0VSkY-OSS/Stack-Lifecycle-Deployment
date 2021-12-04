from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Response

from schemas import schemas
from crud import azure as crud_azure
from crud import user as crud_users
from crud import activityLogs as crud_activity
from security import deps


router = APIRouter()


@router.post("/", status_code=200)
async def create_new_azure_profile(
        azure: schemas.AzureBase,
        response: Response,
        current_user: schemas.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)):

    if not crud_users.is_master(db, current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if "string" in [azure.squad, azure.environment]:
        raise HTTPException(
            status_code=409,
            detail="The squad or environment field must have a value that is not a string.")
    db_azure_account = crud_azure.get_squad_azure_profile(
        db=db, squad=azure.squad, environment=azure.environment)
    if db_azure_account:
        raise HTTPException(
            status_code=409,
            detail="Account already exists")
    try:
        result = crud_azure.create_azure_profile(db=db, azure=azure)
        crud_activity.create_activity_log(
            db=db,
            username=current_user.username,
            squad=current_user.squad,
            action=f'Create Azure Account {azure.subscription_id}'
        )
        return {"result": f'Create Azure account {azure.squad} {azure.environment}'}
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))


@router.get("/")
async def get_all_azure_accounts(
        current_user: schemas.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)):
    if not crud_users.is_master(db, current_user):
        return crud_azure.get_squad_azure_profile(db=db, squad=current_user.squad, environment=None)
    return crud_azure.get_all_azure_profile(db=db)


@router.delete("/{azure_account_id}")
async def delete_azure_account_by_id(
        azure_account_id: int,
        current_user: schemas.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)):

    if not crud_users.is_master(db, current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    result = crud_azure.delete_azure_profile_by_id(
        db=db, azure_profile_id=azure_account_id)
    crud_activity.create_activity_log(
        db=db,
        username=current_user.username,
        squad=current_user.squad,
        action=f'Delete Azure account {azure_account_id}'
    )
    return result
