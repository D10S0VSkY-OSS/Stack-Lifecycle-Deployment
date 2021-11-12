from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException

from schemas import schemas
from security import deps
from crud import user as crud_users
from crud import stacks as crud_stacks
from crud import activityLogs as crud_activity
from helpers.push_task import sync_git, sync_get_vars
from helpers.get_data import check_providers

router = APIRouter()


@router.post("/", response_model=schemas.Stack)
def create_new_stack(
        stack: schemas.StackCreate,
        current_user: schemas.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)):

    if not crud_users.is_superuser(db, current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    name = "default"
    environment = "default"
    squad = "squad"
    branch = stack.branch

    # Checkif stack name providers are supperted
    check_providers(stack_name=stack.stack_name)
    # Check if stack exist
    db_stack = crud_stacks.get_stack_by_name(db, stack_name=stack.stack_name)
    if db_stack:
        raise HTTPException(
            status_code=409,
            detail="The stack name already exist")
    # Push git task to queue squad, all workers are subscribed to this queue
    task = sync_git(
        stack_name=stack.stack_name,
        git_repo=stack.git_repo,
        branch=branch,
        environment=environment,
        squad=squad,
        name=name)
    variables_list = [i for i in task[1]['variable'].keys()]
    try:
        # pesrsist data in db
        result = crud_stacks.create_new_stack(
            db=db,
            stack=stack,
            user_id=current_user.id,
            task_id=task[0],
            var_json=task[1],
            var_list=variables_list,
            squad_access=stack.squad_access
        )

        crud_activity.create_activity_log(
            db=db,
            username=current_user.username,
            squad=current_user.squad,
            action=f'Create Stack {stack.stack_name}'
        )
        return result
    except Exception as err:
        raise HTTPException(status_code=409, detail=f"Duplicate entry {err}")


@router.patch("/{stack_id}", response_model=schemas.Stack)
def update_stack(
        stack_id: int,
        stack: schemas.StackCreate,
        current_user: schemas.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)):
    if not current_user.master:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    name = "default"
    environment = "default"
    squad = "squad"
    branch = stack.branch

    # Checkif stack name providers are supperted
    check_providers(stack_name=stack.stack_name)
    # Check if stack exist
    db_stack = crud_stacks.get_stack_by_name(db, stack_name=stack.stack_name)
    # Push git task to queue squad, all workers are subscribed to this queue
    task = sync_git(
        stack_name=stack.stack_name,
        git_repo=stack.git_repo,
        branch=branch,
        environment=environment,
        squad=squad,
        name=name)
    variables_list = [i for i in task[1]['variable'].keys()]
    try:
        # pesrsist data in db
        result = crud_stacks.update_stack(
            db=db,
            stack_id=stack_id,
            stack=stack,
            user_id=current_user.id,
            task_id=task[0],
            var_json=task[1],
            var_list=variables_list,
            squad_access=stack.squad_access
        )

        crud_activity.create_activity_log(
            db=db,
            username=current_user.username,
            squad=current_user.squad,
            action=f'Update Stack {stack.stack_name}'
        )
        return result
    except Exception as err:
        raise HTTPException(status_code=409, detail=f"Duplicate entry {err}")


@router.get("/")
async def get_all_stacks(
        current_user: schemas.User = Depends(deps.get_current_active_user),
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(deps.get_db)):
    if not current_user.master:
        return crud_stacks.get_all_stacks_by_squad(db=db, squad_access=current_user.squad, skip=skip, limit=limit)
    return crud_stacks.get_all_stacks(db=db, squad_access=current_user.squad, skip=skip, limit=limit)


@router.get("/{stack}")
async def get_stack_by_id_or_name(
        stack,
        current_user: schemas.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)):

    if not stack.isdigit():
        result = crud_stacks.get_stack_by_name(db=db, stack_name=stack)
        if result is None:
            raise HTTPException(status_code=404, detail="stack id not found")
        if not current_user.squad in result.squad_access and not current_user.master and not "*" in result.squad_access:
            raise HTTPException(
                status_code=403, detail="Not enough permissions")
        return result
    result = crud_stacks.get_stack_by_id(db=db, stack_id=stack)
    if result is None:
        raise HTTPException(status_code=404, detail="stack id not found")
    if not current_user.squad in result.squad_access and not current_user.master and not "*" in result.squad_access:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return result


@router.delete("/{stack}")
async def delete_stack_by_id_or_name(
        stack,
        current_user: schemas.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)):
    if not current_user.privilege:
        raise HTTPException(
            status_code=403, detail="Not enough permissions")
    try:
        if not stack.isdigit():
            result = crud_stacks.get_stack_by_name(db=db, stack_name=stack)
            if result is None:
                raise HTTPException(status_code=404, detail="stack id not found")
            if not current_user.squad in result.squad_access and not current_user.master and not "*" in result.squad_access:
                raise HTTPException(
                    status_code=403, detail="Not enough permissions")
            crud_activity.create_activity_log(
                db=db,
                username=current_user.username,
                squad=current_user.squad,
                action=f'Delete Stack {result.stack_name}'
            )
            return crud_stacks.delete_stack_by_name(db=db, stack_name=stack)
        result = crud_stacks.get_stack_by_id(db=db, stack_id=stack)
        if result is None:
            raise HTTPException(status_code=404, detail="stack id not found")
        if not current_user.squad in result.squad_access and not current_user.master and not "*" in result.squad_access:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        crud_activity.create_activity_log(
            db=db,
            username=current_user.username,
            squad=current_user.squad,
            action=f'Delete Stack {result.id}'
        )
        return crud_stacks.delete_stack_by_id(db=db, stack_id=stack)
    except Exception as err:
        return err
