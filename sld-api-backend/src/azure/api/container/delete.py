from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from src.activityLogs.infrastructure import repositories as crud_activity
from src.azure.infrastructure import repositories as crud_azure
from src.shared.security import deps
from src.users.domain.entities import users as schemas_users
from src.azure.domain.entities import azure as schemas_azure
from src.users.infrastructure import repositories as crud_users
from src.shared.domain.exeptions.in_use import ResourceInUseError


async def azure_account_by_id(
    azure_account_id: int,
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> schemas_azure.AzureAccountResponse:

    if not crud_users.is_master(db, current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    filters = schemas_azure.AzureAccountFilter()
    filters.id = azure_account_id
    db_Azure_account = await crud_azure.get_all_azure_profile(db=db, filters=filters)
    if not db_Azure_account:
        raise HTTPException(status_code=404, detail="Account not found")
    try:
        result = await crud_azure.delete_azure_profile_by_id(db=db, azure_account_id=azure_account_id)
        crud_activity.create_activity_log(
            db=db,
            username=current_user.username,
            squad=current_user.squad,
            action=f"Delete Azure account {azure_account_id}",
        )
        return result
    except ResourceInUseError as err:
        raise HTTPException(status_code=409, detail=str(err))
    except Exception as err:
        raise err
