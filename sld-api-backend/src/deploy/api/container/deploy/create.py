from fastapi import Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from src.deploy.domain.entities import deploy as schemas_deploy
from src.deploy.infrastructure import repositories as crud_deploys
from src.shared.helpers.get_data import (
    check_cron_schedule,
    check_deploy_exist,
    check_deploy_task_pending_state,
    check_prefix,
    check_squad_user,
    stack,
)
from src.shared.helpers.push_task import (
    async_deploy,
    async_schedule_add,
    async_schedule_delete,
)
from src.shared.security import deps
from src.tasks.infrastructure import repositories as crud_tasks
from src.users.domain.entities import users as schemas_users
from src.users.infrastructure import repositories as crud_users
from src.worker.domain.entities.worker import DeployParams


async def deploy_infra_by_stack_name(
    response: Response,
    deploy: schemas_deploy.DeployCreate,
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):

    response.status_code = status.HTTP_202_ACCEPTED
    # Get squad from current user
    squad = deploy.squad
    # Get squad from current user
    if not crud_users.is_master(db, current_user):
        current_squad = current_user.squad
        if not check_squad_user(current_squad, [deploy.squad]):
            raise HTTPException(
                status_code=403, detail=f"Not enough permissions in {squad}"
            )
    # Get  credentials by providers supported
    secreto = await check_prefix(
        db, stack_name=deploy.stack_name, environment=deploy.environment, squad=squad
    )
    # Get info from stack data
    stack_data = stack(db, stack_name=deploy.stack_name)
    branch = (
        stack_data.branch
        if deploy.stack_branch == "" or deploy.stack_branch == None
        else deploy.stack_branch
    )
    git_repo = stack_data.git_repo
    tf_ver = stack_data.tf_version
    check_deploy_exist(db, deploy.name, squad, deploy.environment, deploy.stack_name)
    check_deploy_task_pending_state(deploy.name, squad, deploy.environment)
    try:
        # check crontime
        check_cron_schedule(deploy.start_time)
        check_cron_schedule(deploy.destroy_time)
        # push task Deploy to queue and return task_id
        pipeline_deploy = async_deploy(DeployParams(
            git_repo=git_repo,
            name=deploy.name,
            stack_name=deploy.stack_name,
            environment=deploy.environment,
            squad=squad,
            branch=branch,
            version=tf_ver,
            iac_type=stack_data.iac_type if stack_data.iac_type else "terraform",
            variables=deploy.variables,
            secreto=secreto,
            variables_file=deploy.tfvar_file,
            project_path=deploy.project_path,
            user=current_user.username,
        ))
        # Push deploy task data
        db_deploy = crud_deploys.create_new_deploy(
            db=db,
            deploy=deploy,
            stack_branch=branch,
            task_id=pipeline_deploy,
            action="Apply",
            squad=squad,
            user_id=current_user.id,
            username=current_user.username,
        )
        # Push task data
        db_task = crud_tasks.create_task(
            db=db,
            task_id=pipeline_deploy,
            task_name=f"{deploy.stack_name}-{squad}-{deploy.environment}-{deploy.name}",
            user_id=current_user.id,
            deploy_id=db_deploy.id,
            username=current_user.username,
            squad=squad,
            action="Apply",
        )

        return {"task": db_task}
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"{err}")
    finally:
        try:
            async_schedule_delete(db_deploy.id, squad)
            # Add schedule
            async_schedule_add(db_deploy.id, squad)
        except Exception as err:
            print(err)
