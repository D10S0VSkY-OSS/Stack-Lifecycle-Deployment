from fastapi import Depends, HTTPException
from src.shared.security import deps
from sqlalchemy.orm import Session
from src.activityLogs.infrastructure import repositories as crud_activity
from src.aws.infrastructure import repositories as crud_aws
from src.users.domain.entities import users as schemas_users
from src.users.infrastructure import repositories as crud_users


async def aws_account_by_id(
    aws_account_id: int,
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):

    if not crud_users.is_master(db, current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")


    result = crud_aws.delete_aws_profile_by_id(db=db, aws_profile_id=aws_account_id)
    crud_activity.create_activity_log(
        db=db,
        username=current_user.username,
        squad=current_user.squad,
        action=f"Delete AWS account {aws_account_id}",
    )
    return result