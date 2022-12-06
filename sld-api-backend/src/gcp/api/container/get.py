from fastapi import APIRouter, Depends, HTTPException, Response
from src.shared.security import deps
from sqlalchemy.orm import Session
from src.activityLogs.infrastructure import repositories as crud_activity
from src.gcp.domain.entities import gcp as schemas_gcp
from src.gcp.infrastructure import repositories as crud_gcp
from src.users.domain.entities import users as schemas_users
from src.users.infrastructure import repositories as crud_users
from src.deploy.infrastructure import repositories as crud_deploy



async def all_gcloud_accounts(
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):
    if not crud_users.is_master(db, current_user):
        return crud_gcp.get_squad_gcloud_profile(
            db=db, squad=current_user.squad, environment=None
        )
    return crud_gcp.get_all_gcloud_profile(db=db)

