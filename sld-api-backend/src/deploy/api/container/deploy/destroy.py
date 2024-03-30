from fastapi import Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from src.deploy.infrastructure import repositories as crud_deploys
from src.shared.helpers.get_data import (
    check_deploy_state,
    check_deploy_task_pending_state,
    check_prefix,
    check_squad_user,
    deploy,
    stack,
)
from src.shared.helpers.push_task import async_destroy
from src.shared.security import deps
from src.tasks.infrastructure import repositories as crud_tasks
from src.users.domain.entities import users as schemas_users
from src.users.infrastructure import repositories as crud_users
from src.worker.domain.entities.worker import DeployParams


async def destroy_infra(
    deploy_id: int,
    response: Response,
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):

    response.status_code = status.HTTP_202_ACCEPTED
    # Get info from deploy data
    deploy_data = deploy(db, deploy_id=deploy_id)
    squad = deploy_data.squad
    if not crud_users.is_master(db, current_user):
        if not check_squad_user(current_user.squad, [deploy_data.squad]):
            raise HTTPException(
                status_code=403, detail=f"Not enough permissions in {squad}"
            )
    stack_name = deploy_data.stack_name
    environment = deploy_data.environment
    start_time = deploy_data.start_time
    destroy_time = deploy_data.destroy_time
    variables = deploy_data.variables
    tfvar_file = deploy_data.tfvar_file
    project_path = deploy_data.project_path
    name = deploy_data.name
    # Get  credentials by providers supported
    secreto = await check_prefix(
        db, stack_name=stack_name, environment=environment, squad=squad
    )
    # Get info from stack data
    stack_data = stack(db, stack_name=stack_name)
    branch = (
        stack_data.branch
        if deploy_data.stack_branch == "" or deploy_data.stack_branch == None
        else deploy_data.stack_branch
    )
    git_repo = stack_data.git_repo
    tf_ver = stack_data.tf_version
    # check task pending state
    check_deploy_task_pending_state(name, squad, environment, deploy_data.task_id)
    try:
        # Check deploy state
        if not check_deploy_state(deploy_data.task_id):
            raise ValueError("The deployment task is locked and cannot be upgraded. If you wish to proceed with the change, you can force the deletion of the task.")
        # push task destroy to queue and return task_id
        pipeline_destroy = async_destroy(DeployParams(
            git_repo=git_repo,
            name=name,
            stack_name=stack_name,
            environment=environment,
            squad=squad,
            branch=branch,
            version=tf_ver,
            iac_type=stack_data.iac_type if stack_data.iac_type else "terraform",
            variables=variables,
            secreto=secreto,
            tfvar_file=tfvar_file,
            project_path=project_path,
            user=current_user.username,
        ))
        # Push deploy task data
        crud_deploys.update_deploy(
            db=db,
            deploy_id=deploy_id,
            task_id=pipeline_destroy,
            action="Destroy",
            user_id=current_user.id,
            start_time=start_time,
            destroy_time=destroy_time,
            stack_branch=branch,
            tfvar_file=tfvar_file,
            project_path=project_path,
            variables=variables,
            username=current_user.username,
        )
        # Push task data
        db_task = crud_tasks.create_task(
            db=db,
            task_id=pipeline_destroy,
            task_name=f"{stack_name}-{squad}-{environment}-{name}",
            user_id=current_user.id,
            deploy_id=deploy_id,
            username=current_user.username,
            squad=squad,
            action="Destroy",
        )

        return {"task": db_task}
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"{err}")
