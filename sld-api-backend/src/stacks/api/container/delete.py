from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from src.activityLogs.infrastructure import repositories as crud_activity
from src.shared.helpers.get_data import check_squad_stack
from src.shared.security import deps
from src.stacks.infrastructure import repositories as crud_stacks
from src.users.domain.entities import users as schemas_users


async def delete_stack_by_id_or_name(
    stack,
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):
    try:
        if not stack.isdigit():
            result = crud_stacks.get_stack_by_name(db=db, stack_name=stack)
            if result is None:
                raise HTTPException(status_code=404, detail="Stack id not found")
            # Check if the user have permissions for delete stack
            check_squad_stack(db, current_user, current_user.squad, result.squad_access)

            crud_activity.create_activity_log(
                db=db,
                username=current_user.username,
                squad=current_user.squad,
                action=f"Delete Stack {result.stack_name}",
            )
            return crud_stacks.delete_stack_by_name(db=db, stack_name=stack)

        result = crud_stacks.get_stack_by_id(db=db, stack_id=stack)
        if result is None:
            raise HTTPException(status_code=404, detail="Stack id not found")

        # Check if the user have permissions for create stack
        check_squad_stack(db, current_user, current_user.squad, result.squad_access)

        crud_activity.create_activity_log(
            db=db,
            username=current_user.username,
            squad=current_user.squad,
            action=f"Delete Stack {result.id}",
        )
        return crud_stacks.delete_stack_by_id(db=db, stack_id=stack)
    except Exception as err:
        raise err
