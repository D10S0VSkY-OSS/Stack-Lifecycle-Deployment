from fastapi import Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from src.deploy.domain.entities import deploy as schemas_deploy
from src.deploy.infrastructure import repositories as crud_deploys
from src.shared.helpers.get_data import (
    check_cron_schedule,
    check_deploy_state,
    check_prefix,
    check_squad_user,
    deploy,
    stack,
)
from src.shared.helpers.push_task import async_plan
from src.shared.security import deps
from src.tasks.infrastructure import repositories as crud_tasks
from src.users.domain.entities import users as schemas_users
from src.users.infrastructure import repositories as crud_users
from src.worker.domain.entities.worker import DeployParams


async def update_plan_by_id(
    plan_id: int,
    deploy_update: schemas_deploy.DeployUpdate,
    response: Response,
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):

    response.status_code = status.HTTP_202_ACCEPTED
    # Get info from deploy data
    deploy_data = deploy(db, deploy_id=plan_id)
    squad = deploy_data.squad
    stack_name = deploy_data.stack_name
    environment = deploy_data.environment
    name = deploy_data.name
    if not crud_users.is_master(db, current_user):
        if not check_squad_user(current_user.squad, [squad]):
            raise HTTPException(
                status_code=403, detail=f"Not enough permissions in {squad}"
            )
    # Get  credentials by providers supported
    secreto = await check_prefix(
        db, stack_name=stack_name, environment=environment, squad=squad
    )
    # Get info from stack data
    stack_data = stack(db, stack_name=stack_name)
    branch = (
        stack_data.branch
        if deploy_update.stack_branch == ""
        else deploy_update.stack_branch
    )
    git_repo = stack_data.git_repo
    tf_ver = stack_data.tf_version
    try:
        # check crontime
        check_cron_schedule(deploy_update.start_time)
        check_cron_schedule(deploy_update.destroy_time)
        # Check deploy state
        if not check_deploy_state(deploy_data.task_id):
            raise ValueError("The deployment task is locked and cannot be upgraded. If you wish to proceed with the change, you can force the deletion of the task.")
        # push task Deploy to queue and return task_id
        pipeline_plan = async_plan(DeployParams(
            git_repo=git_repo,
            name=name,
            stack_name=stack_name,
            environment=environment,
            squad=squad,
            branch=branch,
            iac_type=stack_data.iac_type if stack_data.iac_type else "terraform",
            version=tf_ver,
            variables=deploy_update.variables,
            secreto=secreto,
            variables_file=deploy_update.tfvar_file,
            project_path=deploy_update.project_path,
            user=current_user.username,
        ))
        # Push deploy task data
        crud_deploys.update_deploy(
            db=db,
            deploy_id=plan_id,
            task_id=pipeline_plan,
            action="Plan",
            user_id=current_user.id,
            stack_branch=deploy_update.stack_branch,
            tfvar_file=deploy_update.tfvar_file,
            project_path=deploy_update.project_path,
            variables=deploy_update.variables,
            start_time=deploy_update.start_time,
            destroy_time=deploy_update.destroy_time,
            username=current_user.username,
        )
        action = "Plan"
        # Push task data
        db_task = crud_tasks.create_task(
            db=db,
            task_id=pipeline_plan,
            task_name=f"{stack_name}-{squad}-{environment}-{name}",
            user_id=current_user.id,
            deploy_id=plan_id,
            username=current_user.username,
            squad=squad,
            action=action,
        )

        return {"task": pipeline_plan}
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"{err}")
