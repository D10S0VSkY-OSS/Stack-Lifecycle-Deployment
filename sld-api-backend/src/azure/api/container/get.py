from fastapi import Depends
from sqlalchemy.orm import Session

from src.azure.infrastructure import repositories as crud_azure
from src.shared.security import deps
from src.users.domain.entities import users as schemas_users
from src.users.infrastructure import repositories as crud_users
from src.azure.domain.entities import azure as schemas_azure


async def get_all_azure_accounts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    filters: schemas_azure.AzureAccountFilter = Depends(schemas_azure.AzureAccountFilter),
):
    if not crud_users.is_master(db, current_user):
        filters.squad = current_user.squad
    return await crud_azure.get_all_azure_profile(db=db, filters=filters, skip=skip, limit=limit)
