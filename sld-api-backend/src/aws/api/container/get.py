from fastapi import Depends
from src.shared.security import deps
from sqlalchemy.orm import Session
from src.aws.infrastructure import repositories as crud_aws
from src.users.domain.entities import users as schemas_users
from src.users.infrastructure import repositories as crud_users



async def get_all_aws_accounts(
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):
    # Check if the user has privileges
    if not crud_users.is_master(db, current_user):
        return crud_aws.get_squad_aws_profile(
            db=db, squad=current_user.squad, environment=None
        )
    return crud_aws.get_all_aws_profile(db=db)



