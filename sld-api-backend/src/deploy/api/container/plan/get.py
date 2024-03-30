from fastapi import Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from src.shared.helpers.get_data import (
    check_deploy_state,
    check_prefix,
    check_squad_user,
    deploy,
    stack,
)
from src.shared.helpers.push_task import async_plan
from src.shared.security import deps
from src.users.domain.entities import users as schemas_users
from src.users.infrastructure import repositories as crud_users


async def get_plan_by_id_deploy(
    deploy_id: int,
    response: Response,
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):

    response.status_code = status.HTTP_202_ACCEPTED
    deploy_data = deploy(db, deploy_id=deploy_id)
    if not crud_users.is_master(db, current_user):
        if not check_squad_user(current_user.squad, [deploy_data.squad]):
            raise HTTPException(
                status_code=403, detail=f"Not enough permissions in {deploy_data.squad}"
            )
    # Get  credentials by providers supported
    secreto = await check_prefix(
        db,
        stack_name=deploy_data.stack_name,
        environment=deploy_data.environment,
        squad=deploy_data.squad,
    )
    # Get info from stack data
    stack_data = stack(db, stack_name=deploy_data.stack_name)
    branch = deploy_data.stack_branch
    git_repo = stack_data.git_repo
    tf_ver = stack_data.tf_version
    try:
        # Check deploy state
        if not check_deploy_state(deploy_data.task_id):
            raise ValueError("The deployment task is locked and cannot be upgraded. If you wish to proceed with the change, you can force the deletion of the task.")
        # push task Deploy to queue and return task_id
        pipeline_plan = async_plan(
            git_repo,
            deploy_data.name,
            deploy_data.stack_name,
            deploy_data.environment,
            deploy_data.squad,
            branch,
            tf_ver,
            deploy_data.variables,
            secreto,
            deploy_data.tfvar_file,
            deploy_data.project_path,
        )
        return {"task": pipeline_plan}
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"{err}")
