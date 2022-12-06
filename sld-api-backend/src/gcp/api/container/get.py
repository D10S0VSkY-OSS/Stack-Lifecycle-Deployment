from fastapi import Depends
from sqlalchemy.orm import Session

from src.gcp.infrastructure import repositories as crud_gcp
from src.shared.security import deps
from src.users.domain.entities import users as schemas_users
from src.users.infrastructure import repositories as crud_users


async def all_gcloud_accounts(
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):
    if not crud_users.is_master(db, current_user):
        return crud_gcp.get_squad_gcloud_profile(
            db=db, squad=current_user.squad, environment=None
        )
    return crud_gcp.get_all_gcloud_profile(db=db)
