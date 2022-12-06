from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from src.deploy.infrastructure import repositories as crud_deploys
from src.shared.helpers.get_data import check_squad_user
from src.shared.security import deps
from src.stacks.infrastructure import repositories as crud_stacks
from src.users.domain.entities import users as schemas_users
from src.users.infrastructure import repositories as crud_users


async def get_json(
    stack,
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):
    """
    Pass the name of the stack or the id, and I will return the variables supported by the stack as json format
    """
    try:
        if stack.isdigit():
            result = crud_stacks.get_stack_by_id(db=db, stack_id=stack)
            if result == None:
                raise HTTPException(
                    status_code=404, detail=f"Not found"
                )
            if not crud_users.is_master(db, current_user):
                if "*" not in result.squad_access:
                    if not check_squad_user(current_user.squad, result.squad_access):
                        raise HTTPException(
                            status_code=403, detail=f"Not enough permissions"
                        )
            return result.var_json.get("variable")
        else:
            result = crud_stacks.get_stack_by_name(db=db, stack_name=stack)
            if result == None:
                raise HTTPException(
                    status_code=404, detail=f"Not found"
                )
            if not crud_users.is_master(db, current_user):
                if "*" not in result.squad_access:
                    if not check_squad_user(current_user.squad, result.squad_access):
                        raise HTTPException(
                            status_code=403, detail=f"Not enough permissions"
                        )
            return result.var_json.get("variable")
    except Exception as err:
        raise err


async def get_list(
    stack,
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):
    """
    Pass the name of the stack or the id, and I will return the variables supported by the stack as list format
    """
    try:
        if stack.isdigit():
            result = crud_stacks.get_stack_by_id(db=db, stack_id=stack)
            if result == None:
                raise HTTPException(
                    status_code=404, detail=f"Not found"
                )
            if not crud_users.is_master(db, current_user):
                if "*" not in result.squad_access:
                    if not check_squad_user(current_user.squad, result.squad_access):
                        raise HTTPException(
                            status_code=403, detail=f"Not enough permissions"
                        )
            return result.var_list
        else:
            result = crud_stacks.get_stack_by_name(db=db, stack_name=stack)
            if result == None:
                raise HTTPException(
                    status_code=404, detail=f"Not found"
                )
            if not crud_users.is_master(db, current_user):
                if "*" not in result.squad_access:
                    if not check_squad_user(current_user.squad, result.squad_access):
                        raise HTTPException(
                            status_code=403, detail=f"Not enough permissions"
                        )
            return result.var_list
    except Exception as err:
        raise err


async def get_deploy_by_id(
    deploy_id: int,
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):

    try:
        result = crud_deploys.get_deploy_by_id(db=db, deploy_id=deploy_id)
        if result == None:
            raise HTTPException(
                status_code=404, detail=f"Not found"
            )
        if not crud_users.is_master(db, current_user):
            if not check_squad_user(current_user.squad, [result.squad]):
                raise HTTPException(
                    status_code=403, detail=f"Not enough permissions"
                )
        return result.variables
    except Exception as err:
        raise err
