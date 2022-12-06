from fastapi import BackgroundTasks, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from src.deploy.domain.entities import schedule as schemas_schedule
from src.deploy.infrastructure import repositories as crud_deploys
from src.shared.helpers.get_data import check_cron_schedule, check_squad_user, deploy
from src.shared.helpers.push_task import async_schedule_update
from src.shared.security import deps
from src.tasks.infrastructure import repositories as crud_tasks
from src.users.domain.entities import users as schemas_users
from src.users.infrastructure import repositories as crud_users


async def update_schedule(
    deploy_id: int,
    background_tasks: BackgroundTasks,
    deploy_update: schemas_schedule.ScheduleUpdate,
    response: Response,
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):

    response.status_code = status.HTTP_202_ACCEPTED

    # Get info from deploy data
    deploy_data = deploy(db, deploy_id=deploy_id)
    squad = deploy_data.squad
    stack_name = deploy_data.stack_name
    environment = deploy_data.environment
    name = deploy_data.name
    if not crud_users.is_master(db, current_user):
        if not check_squad_user(current_user.squad, [squad]):
            raise HTTPException(
                status_code=403, detail=f"Not enough permissions in {squad}"
            )
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
            destroy_time=deploy_update.destroy_time,
        )
        # Push task data
        db_task = crud_tasks.create_task(
            db=db,
            task_id=pipeline_schedule,
            task_name=f"{stack_name}-{squad}-{environment}-{name}",
            user_id=current_user.id,
            deploy_id=deploy_id,
            username=current_user.username,
            squad=squad,
            action="UpdateSchedule",
        )

        return {"task_id": pipeline_schedule}
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"{err}")
