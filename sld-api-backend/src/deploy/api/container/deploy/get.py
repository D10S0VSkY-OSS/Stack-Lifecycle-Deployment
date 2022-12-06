from fastapi import (APIRouter, BackgroundTasks, Depends, HTTPException,
                     Response, status)
from src.shared.helpers.get_data import (check_cron_schedule, check_deploy_exist,
                              check_deploy_state,
                              check_deploy_task_pending_state,check_prefix,
                              check_squad_user, deploy, deploy_squad, stack)
from src.shared.helpers.push_task import (async_deploy, async_destroy, async_output,
                               async_schedule_add, async_schedule_delete,
                               async_show, async_unlock)
from src.shared.security import deps
from sqlalchemy.orm import Session
from src.deploy.domain.entities import deploy as schemas_deploy
from src.deploy.infrastructure import repositories as crud_deploys
from src.tasks.infrastructure import repositories as crud_tasks
from src.users.domain.entities import users as schemas_users
from src.users.infrastructure import repositories as crud_users



async def unlock_deploy(
    deploy_id: int,
    db: Session = Depends(deps.get_db),
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
):
    # Get info from deploy data
    deploy_data = deploy(db, deploy_id=deploy_id)
    squad = deploy_data.squad
    if not crud_users.is_master(db, current_user):
        if not check_squad_user(current_user.squad, [squad]):
            raise HTTPException(
                status_code=403, detail=f"Not enough permissions in {squad}"
            )
    try:
        stack_name = deploy_data.stack_name
        environment = deploy_data.environment
        name = deploy_data.name
        # Get  credentials by providers supported
        return {"task": async_unlock(stack_name, squad, environment, name)}
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"{err}")


async def get_all_deploys(
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
):
    try:
        if not crud_users.is_master(db, current_user):
            squad = current_user.squad
            return crud_deploys.get_all_deploys_by_squad(
                db=db, squad=squad, skip=skip, limit=limit
            )
        return crud_deploys.get_all_deploys(db=db, skip=skip, limit=limit)
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"{err}")


async def get_deploy_by_id(
    deploy_id: int,
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):

    result = crud_deploys.get_deploy_by_id(db=db, deploy_id=deploy_id)
    if not crud_users.is_master(db, current_user):
        if not check_squad_user(current_user.squad, [result.squad]):
            raise HTTPException(
                status_code=403, detail=f"Not enough permissions in {result.squad}"
            )
    try:
        if result is None:
            raise HTTPException(status_code=404, detail="Deploy id Not Found")
        return result
    except Exception as err:
        print(err)
        raise HTTPException(status_code=404, detail=f"{err}")


async def get_show(
    deploy_id: int,
    db: Session = Depends(deps.get_db),
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
):
    # Get info from deploy data
    if crud_users.is_master(db, current_user):
        deploy_data = deploy(db, deploy_id=deploy_id)
        squad = deploy_data.squad
    else:
        # Get squad from current user
        squad = current_user.squad
        deploy_data = deploy_squad(db, deploy_id=deploy_id, squad=squad)
    stack_name = deploy_data.stack_name
    environment = deploy_data.environment
    name = deploy_data.name
    try:
        return {"task": async_show(stack_name, squad, environment, name)}
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"{err}")


async def get_output(
    deploy_id: int,
    db: Session = Depends(deps.get_db),
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
):
    # Get info from deploy data
    deploy_data = deploy(db, deploy_id=deploy_id)
    squad = deploy_data.squad
    if not crud_users.is_master(db, current_user):
        if not check_squad_user(current_user.squad, [squad]):
            raise HTTPException(
                status_code=403, detail=f"Not enough permissions in {squad}"
            )
    try:
        stack_name = deploy_data.stack_name
        environment = deploy_data.environment
        name = deploy_data.name
        # Get  credentials by providers supported
        return {"task": async_output(stack_name, squad, environment, name)}
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"{err}")

