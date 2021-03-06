from sqlalchemy.orm import Session
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, status

from schemas import schemas
from crud import deploys as crud_deploys
from crud import tasks as crud_tasks
from security import deps
from security import tokens
from helpers.get_data import check_cron_schedule
from helpers.get_data import check_deploy_exist, check_deploy_state
from helpers.get_data import stack, deploy, deploy_squad, check_deploy_exist
from helpers.push_task import async_schedule_list, async_schedule_get, async_schedule_add, async_schedule_delete, async_schedule_update


router = APIRouter()


@router.get("/list/", status_code=202)
async def list_schedules(
        db: Session = Depends(deps.get_db),
        current_user: schemas.User = Depends(deps.get_current_active_user)):
    squad = current_user.squad
    try:
        return {"task_id": async_schedule_list(squad=squad)}
    except Exception as err:
        raise HTTPException(
            status_code=400,
            detail=f"{err}")


@router.get("/{deploy_id}", status_code=202)
async def get_schedule(
        deploy_id: int,
        db: Session = Depends(deps.get_db),
        current_user: schemas.User = Depends(deps.get_current_active_user)):
    # Get info from deploy data
    if current_user.master:
        deploy_data = deploy(db, deploy_id=deploy_id)
        squad = deploy_data.squad
    else:
        # Get squad from current user
        squad = current_user.squad
        deploy_data = deploy_squad(db, deploy_id=deploy_id, squad=squad)
    deploy_name = deploy_data.id
    try:
        return {"task_id": async_schedule_get(deploy_name=deploy_name, squad=squad)}
    except Exception as err:
        raise HTTPException(
            status_code=400,
            detail=f"{err}")


@router.post("/{deploy_id}", status_code=202)
async def add_schedule(
        deploy_id: int,
        db: Session = Depends(deps.get_db),
        current_user: schemas.User = Depends(deps.get_current_active_user)):
    # Get info from deploy data
    if current_user.master:
        deploy_data = deploy(db, deploy_id=deploy_id)
        squad = deploy_data.squad
    else:
        # Get squad from current user
        squad = current_user.squad
        deploy_data = deploy_squad(db, deploy_id=deploy_id, squad=squad)
    deploy_name = deploy_data.id
    try:
        return {"task_id":async_schedule_add(deploy_name=deploy_name, squad=squad)}
    except Exception as err:
        raise HTTPException(
            status_code=400,
            detail=f"{err}")


@router.delete("/{deploy_id}", status_code=202)
async def delete_schedule(
        deploy_id: int,
        db: Session = Depends(deps.get_db),
        current_user: schemas.User = Depends(deps.get_current_active_user)):
    # Get info from deploy data
    if current_user.master:
        deploy_data = deploy(db, deploy_id=deploy_id)
        squad = deploy_data.squad
    else:
        # Get squad from current user
        squad = current_user.squad
        deploy_data = deploy_squad(db, deploy_id=deploy_id, squad=squad)
    deploy_name = deploy_data.id
    try:
        return {"task_id":async_schedule_delete(deploy_name=deploy_name, squad=squad)}
    except Exception as err:
        raise HTTPException(
            status_code=400,
            detail=f"{err}")


@router.patch("/{deploy_id}", status_code=202)
async def update_schedule(
        deploy_id: int,
        background_tasks: BackgroundTasks,
        deploy_update: schemas.ScheduleUpdate,
        response: Response,
        current_user: schemas.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)):

    response.status_code = status.HTTP_202_ACCEPTED

    # Get info from deploy data
    if current_user.master:
        deploy_data = deploy(db, deploy_id=deploy_id)
        squad = deploy_data.squad
    else:
        # Get squad from current user
        squad = current_user.squad
        deploy_data = deploy_squad(db, deploy_id=deploy_id, squad=squad)
    stack_name = deploy_data.stack_name
    environment = deploy_data.environment
    squad = deploy_data.squad
    name = deploy_data.name
    try:
        # check crontime
        check_cron_schedule(deploy_update.start_time)
        check_cron_schedule(deploy_update.destroy_time)
        # push task Deploy to queue and return task_id
        pipeline_schedule = async_schedule_update(deploy_id)
        # Update db data time schedule
        crud_deploys.update_schedule(
            db=db,
            deploy_id=deploy_id,
            start_time=deploy_update.start_time,
            destroy_time=deploy_update.destroy_time)
        # Push task data
        db_task = crud_tasks.create_task(
            db=db,
            task_id=pipeline_schedule,
            task_name=f"{stack_name}-{squad}-{environment}-{name}",
            user_id=current_user.id,
            deploy_id=deploy_id,
            username=current_user.username,
            squad=squad,
            action="UpdateSchedule")

        return {"task_id": pipeline_schedule}
    except Exception as err:
        raise HTTPException(
            status_code=400,
            detail=f"{err}")
