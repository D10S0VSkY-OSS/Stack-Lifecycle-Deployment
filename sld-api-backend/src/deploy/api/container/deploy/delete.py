from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from src.deploy.infrastructure import repositories as crud_deploys
from src.shared.helpers.get_data import (
    check_deploy_state,
    check_prefix,
    check_squad_user,
    deploy,
    stack,
)
from src.shared.helpers.push_task import async_destroy, async_schedule_delete
from src.shared.security import deps
from src.tasks.infrastructure import repositories as crud_tasks
from src.users.domain.entities import users as schemas_users
from src.users.infrastructure import repositories as crud_users
from src.worker.domain.entities.worker import DeployParams


async def delete_infra_by_id(
    deploy_id: int,
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):

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
    name = deploy_data.name
    tfvar_file = deploy_data.tfvar_file
    project_path = deploy_data.project_path
    variables = deploy_data.variables
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
    try:
        # Check deploy state
        if not check_deploy_state(deploy_data.task_id):
            raise ValueError("The deployment task is locked and cannot be upgraded. If you wish to proceed with the change, you can force the deletion of the task.")
        # Delete deploy db by id
        crud_deploys.delete_deploy_by_id(db=db, deploy_id=deploy_id, squad=squad)
        # push task destroy to queue and return task_id
        pipeline_destroy = async_destroy(DeployParams(
            git_repo=git_repo,
            name=name,
            stack_name=stack_name,
            environment=environment,
            squad=squad,
            branch=branch,
            iac_type=stack_data.iac_type if stack_data.iac_type else "terraform",
            version=tf_ver,
            variables=variables,
            secreto=secreto,
            tfvar_file=tfvar_file,
            project_path=project_path,
            user=current_user.username,
        ))
        # Push task data
        db_task = crud_tasks.create_task(
            db=db,
            task_id=pipeline_destroy,
            task_name=f"{deploy_data.stack_name}-{squad}-{deploy_data.environment}-{deploy_data.name}",
            user_id=current_user.id,
            deploy_id=deploy_id,
            username=current_user.username,
            squad=squad,
            action="Delete",
        )
        return {"task": db_task}

    except Exception as err:
        raise HTTPException(status_code=400, detail=f"{err}")
    finally:
        async_schedule_delete(deploy_id, squad)
