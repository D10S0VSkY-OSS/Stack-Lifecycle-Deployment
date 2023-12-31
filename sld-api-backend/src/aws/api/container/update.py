from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from src.activityLogs.infrastructure import repositories as crud_activity
from src.aws.domain.entities import aws as schemas_aws
from src.aws.infrastructure import repositories as crud_aws
from src.shared.security import deps
from src.users.domain.entities import users as schemas_users
from src.users.infrastructure import repositories as crud_users
from src.shared.domain.exeptions.in_use import ResourceInUseError


async def update_aws_account(
    aws_account_id: int,
    aws: schemas_aws.AwsAccountUpdate,
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> schemas_aws.AwsAsumeProfile:
    if not crud_users.is_master(db, current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    try:
        filters = schemas_aws.AwsAccountFilter()
        filters.id = aws_account_id
        db_aws_account = await crud_aws.get_all_aws_profile(db=db, filters=filters)
        if not db_aws_account:
            raise HTTPException(status_code=404, detail="Account not found")
        result = await crud_aws.update_aws_profile(db=db, aws_account_id=aws_account_id, updated_aws=aws)
        crud_activity.create_activity_log(
            db=db,
            username=current_user.username,
            squad=current_user.squad,
            action=f"Update AWS account {aws.squad} {aws.environment}",
        )
        return result
    except ResourceInUseError as err:
        raise HTTPException(status_code=409, detail=str(err))
    except Exception as err:
        raise err
