from fastapi import Depends
from sqlalchemy.orm import Session

from src.gcp.infrastructure import repositories as crud_gcp
from src.gcp.domain.entities import gcp as schemas_gcp
from src.shared.security import deps
from src.users.domain.entities import users as schemas_users
from src.users.infrastructure import repositories as crud_users


async def get_all_gcp_accounts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    filters: schemas_gcp.GcloudAccountFilter = Depends(schemas_gcp.GcloudAccountFilter),

) -> list[schemas_gcp.GcloudResponse]:
    if not crud_users.is_master(db, current_user):
        filters.squad = current_user.squad
    return await crud_gcp.get_all_gcloud_profile(db=db, filters=filters, skip=skip, limit=limit)
