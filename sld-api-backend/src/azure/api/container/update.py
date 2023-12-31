from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from src.activityLogs.infrastructure import repositories as crud_activity
from src.azure.domain.entities import azure as schemas_azure
from src.azure.infrastructure import repositories as crud_azure
from src.shared.security import deps
from src.users.domain.entities import users as schemas_users
from src.users.infrastructure import repositories as crud_users
from src.shared.domain.exeptions.in_use import ResourceInUseError


async def update_azure_account(
    azure_account_id: int,
    azure: schemas_azure.AzureAccountUpdate,
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> schemas_azure.AzureAccountResponse:
    if not crud_users.is_master(db, current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    try:
        filters = schemas_azure.AzureAccountFilter()
        filters.id = azure_account_id
        db_azure_account = await crud_azure.get_all_azure_profile(db=db, filters=filters)
        if not db_azure_account:
            raise HTTPException(status_code=404, detail="Account not found")
        result = await crud_azure.update_azure_profile(db=db, azure_account_id=azure_account_id, updated_azure=azure)
        crud_activity.create_activity_log(
            db=db,
            username=current_user.username,
            squad=current_user.squad,
            action=f"Update azure account {azure.squad} {azure.environment}",
        )
        return result
    except ResourceInUseError as err:
        raise HTTPException(status_code=409, detail=str(err))
    except Exception as err:
        raise err
