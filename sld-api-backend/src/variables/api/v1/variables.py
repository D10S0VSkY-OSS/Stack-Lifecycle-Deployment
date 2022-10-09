from src.deploy.infrastructure import repositories as crud_deploys
from src.stacks.infrastructure import repositories as crud_stacks
from src.users.infrastructure import repositories as crud_users
from src.users.domain.entities import users as schemas_users
from fastapi import APIRouter, Depends, HTTPException
from helpers.get_data import check_squad_user
from security import deps
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/json")
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
            return result.var_json.get("variable")
        else:
            result = crud_stacks.get_stack_by_name(db=db, stack_name=stack)
        return result.var_json.get("variable")
    except Exception as err:
        raise HTTPException(status_code=404, detail=f"{err}")


@router.get("/list")
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
            return result.var_list
        else:
            result = crud_stacks.get_stack_by_name(db=db, stack_name=stack)
        return result.var_list
    except Exception as err:
        raise HTTPException(status_code=404, detail=f"{err}")


@router.get("/deploy/{deploy_id}")
async def get_deploy_by_id(
    deploy_id: int,
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):

    result = crud_deploys.get_deploy_by_id(db=db, deploy_id=deploy_id)
    if not crud_users.is_master(db, current_user):
        if not check_squad_user(current_user.squad, [result.squad]):
            raise HTTPException(
                status_code=403, detail=f"Not enough permissions in {squad}"
            )
    try:
        if result is None:
            raise Exception("Deploy id Not Found")
        return result.variables
    except Exception as err:
        raise HTTPException(status_code=404, detail=f"{err}")
