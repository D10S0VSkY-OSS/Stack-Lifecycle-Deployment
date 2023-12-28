from fastapi import Depends
from sqlalchemy.orm import Session

from src.aws.infrastructure import repositories as crud_aws
from src.aws.domain.entities import aws as schemas_aws
from src.shared.security import deps
from src.users.domain.entities import users as schemas_users
from src.users.infrastructure import repositories as crud_users


async def get_all_aws_accounts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    filters: schemas_aws.AwsAccountFilter = Depends(schemas_aws.AwsAccountFilter),

) -> list[schemas_aws.AwsAccountResponse]:
    if not crud_users.is_master(db, current_user):
        filters.squad = current_user.squad
    return await crud_aws.get_all_aws_profile(db=db, filters=filters, skip=skip, limit=limit)
