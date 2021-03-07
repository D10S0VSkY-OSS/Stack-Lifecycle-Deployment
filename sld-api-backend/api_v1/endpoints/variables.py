from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException


from schemas import schemas
from crud import stacks as crud_stacks
from crud import deploys as crud_deploys
from security import deps


router = APIRouter()


@router.get("/json")
async def get_json(
        stack, 
        current_user: schemas.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)):
    '''
    Pass the name of the stack or the id, and I will return the variables supported by the stack as json format
    '''
    try:
        if stack.isdigit():
            result = crud_stacks.get_stack_by_id(db=db, stack_id=stack)
            return result.var_json.get("variable")
        else:
            result = crud_stacks.get_stack_by_name(db=db, stack_name=stack)
        return result.var_json.get("variable")
    except Exception as err:
        raise HTTPException(
            status_code=404,
            detail=f"{err}")


@ router.get("/list")
async def get_list(
        stack,
        current_user: schemas.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)):
    '''
    Pass the name of the stack or the id, and I will return the variables supported by the stack as list format
    '''
    try:
        if stack.isdigit():
            result = crud_stacks.get_stack_by_id(db=db, stack_id=stack)
            return result.var_list
        else:
            result = crud_stacks.get_stack_by_name(db=db, stack_name=stack)
        return result.var_list
    except Exception as err:
        raise HTTPException(
            status_code=404,
            detail=f"{err}")

@router.get("/deploy/{deploy_id}")
async def get_deploy_by_id(
        deploy_id: int,
        current_user: schemas.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)):
    try:
        if current_user.master:
            result = crud_deploys.get_deploy_by_id(db=db, deploy_id=deploy_id)
        else:
            squad = current_user.squad
            result = crud_deploys.get_deploy_by_id_squad(db=db, deploy_id=deploy_id, squad=squad)
        if result is None:
            raise Exception("Deploy id Not Found")
        return result.variables
    except Exception as err:
        raise HTTPException(
            status_code=404,
            detail=f"{err}")

