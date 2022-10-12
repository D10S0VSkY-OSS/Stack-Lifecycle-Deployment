from fastapi import APIRouter, Depends, HTTPException, Response
from security import deps
from sqlalchemy.orm import Session
from src.activityLogs.infrastructure import repositories as crud_activity
from src.custom_providers.domain.entities import custom_providers as schemas_custom_provider
from src.custom_providers.infrastructure import repositories as crud_custom_provider
from src.users.domain.entities import users as schemas_users
from src.users.infrastructure import repositories as crud_users

router = APIRouter()


@router.post("/", status_code=200)
async def create_new_gcloud_profile(
    custom_provider: schemas_custom_provider.CustomProviderBase,
    response: Response,
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):
    if not crud_users.is_master(db, current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if "string" in [custom_provider.squad, custom_provider.environment]:
        raise HTTPException(
            status_code=409,
            detail="The squad or environment field must have a value that is not a string.",
        )
    db_custom_provider_account = crud_custom_provider.get_squad_custom_provider_profile(
        db=db, squad=custom_provider.squad, environment=custom_provider.environment
    )
    if db_custom_provider_account:
        raise HTTPException(status_code=409, detail="Account already exists")
    try:
        result = crud_custom_provider.create_custom_provider_profile(
            db=db,
            squad=custom_provider.squad,
            environment=custom_provider.environment,
            configuration_keyfile_json=custom_provider.configuration,
        )
        crud_activity.create_activity_log(
            db=db,
            username=current_user.username,
            squad=current_user.squad,
            action=f"Create custom provider account {result.id}",
        )
        return {"result": f"Create custom provider account {custom_provider.squad} {custom_provider.environment}"}
    except Exception as err:
        raise HTTPException(status_code=400, detail=err)


@router.get("/")
async def get_all_custom_providers_accounts(
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):
    if not crud_users.is_master(db, current_user):
        return crud_custom_provider.get_squad_custom_provider_profile(
            db=db, squad=current_user.squad, environment=None
        )
    return crud_custom_provider.get_all_custom_profile(db=db)


@router.delete("/{custom_provider_id}")
async def delete_custom_provider_account_by_id(
    custom_provider_id,
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):
    if not crud_users.is_master(db, current_user):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    result = crud_custom_provider.delete_custom_profile_by_id(
        db=db, custom_profile_id=custom_provider_id
    )
    crud_activity.create_activity_log(
        db=db,
        username=current_user.username,
        squad=current_user.squad,
        action=f"Delete custom provider account {custom_provider_id} squad",
    )
    return result
