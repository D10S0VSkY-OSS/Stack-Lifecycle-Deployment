from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from src.activityLogs.infrastructure import repositories as crud_activity
from src.aws.domain.entities import aws as schemas_aws
from src.aws.infrastructure import repositories as crud_aws
from src.shared.security import deps
from src.users.domain.entities import users as schemas_users
from src.users.infrastructure import repositories as crud_users


async def update_aws_account(
    deploy_id: int,
    aws: schemas_aws.AwsAsumeProfile,
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):
    # Check if the user has privileges
    if not crud_users.is_master(db, current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if "string" in [aws.squad, aws.environment]:
        raise HTTPException(
            status_code=409,
            detail="The squad or environment field must have a value that is not a string.",
        )

    try:
        filters = schemas_aws.AwsAccountFilter()
        filters.id = deploy_id
        db_aws_account = crud_aws.get_all_aws_profile(db=db, filters=filters)

        if db_aws_account:
            # If the AWS profile already exists, perform an update
            aws_id_to_update = db_aws_account[0].id  # Assuming you want to update the first matching profile
            return await crud_aws.update_aws_profile(db=db, aws_id=aws_id_to_update, updated_aws=aws)

    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))
