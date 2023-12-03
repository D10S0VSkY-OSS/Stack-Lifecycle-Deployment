from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from src.shared.helpers.get_data import check_squad_user
from src.shared.security import deps
from src.stacks.infrastructure import repositories as crud_stacks
from src.users.domain.entities import users as schemas_users
from src.users.infrastructure import repositories as crud_users


async def get_all_stacks(
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
):
    if not crud_users.is_master(db, current_user):
        return crud_stacks.get_all_stacks_by_squad(
            db=db, squad_access=current_user.squad, skip=skip, limit=limit
        )
    return crud_stacks.get_all_stacks(
        db=db, squad_access=current_user.squad, skip=skip, limit=limit
    )


async def get_stack_by_id_or_name(
    stack,
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):

    if not stack.isdigit():
        result = crud_stacks.get_stack_by_name(db=db, stack_name=stack)
        if not crud_users.is_master(db, current_user):
            if result is None:
                raise HTTPException(status_code=404, detail="stack id not found")
            if (
                not check_squad_user(current_user.squad, result.squad_access)
                and "*" not in result.squad_access
            ):
                raise HTTPException(
                    status_code=403,
                    detail=f"Not enough permissions in {result.squad_access}",
                )
        return result

    result = crud_stacks.get_stack_by_id(db=db, stack_id=stack)
    if result is None:
        raise HTTPException(status_code=404, detail="stack id not found")
    if not crud_users.is_master(db, current_user):
        if (
            not check_squad_user(current_user.squad, result.squad_access)
            and "*" not in result.squad_access
        ):
            raise HTTPException(
                status_code=403,
                detail=f"Not enough permissions in {result.squad_access}",
            )

    return result
