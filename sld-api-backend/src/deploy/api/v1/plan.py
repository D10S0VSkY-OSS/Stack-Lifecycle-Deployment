from fastapi import (APIRouter, BackgroundTasks, Depends, HTTPException,
                     Response, status)
from src.shared.helpers.get_data import (check_cron_schedule, check_deploy_exist,
                              check_deploy_state, check_squad_user, deploy,
                              stack, check_prefix)
from src.shared.helpers.push_task import async_plan
from src.shared.security import deps
from sqlalchemy.orm import Session
from src.deploy.domain.entities import deploy as schemas_deploy
from src.deploy.domain.entities import plan as schemas_plan
from src.deploy.infrastructure import repositories as crud_deploys
from src.tasks.infrastructure import repositories as crud_tasks
from src.users.domain.entities import users as schemas_users
from src.users.infrastructure import repositories as crud_users

router = APIRouter()


@router.post("/", status_code=202)
async def plan_infra_by_stack_name(
    response: Response,
    background_tasks: BackgroundTasks,
    deploy: schemas_plan.PlanCreate,
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):
    response.status_code = status.HTTP_202_ACCEPTED

    squad = deploy.squad
    # Get squad from current user
    if not crud_users.is_master(db, current_user):
        current_squad = current_user.squad
        if not check_squad_user(current_squad, [deploy.squad]):
            raise HTTPException(
                status_code=403, detail=f"Not enough permissions in {squad}"
            )
    # Get  credentials by providers supported
    secreto = check_prefix(
        db, stack_name=deploy.stack_name, environment=deploy.environment, squad=squad
    )
    # Get info from stack data
    stack_data = stack(db, stack_name=deploy.stack_name)
    branch = stack_data.branch if deploy.stack_branch == "" else deploy.stack_branch
    git_repo = stack_data.git_repo
    tf_ver = stack_data.tf_version
    check_deploy_exist(db, deploy.name, squad, deploy.environment, deploy.stack_name)
    try:
        # push task Deploy to queue and return task_id
        pipeline_plan = async_plan(
            git_repo,
            deploy.name,
            deploy.stack_name,
            deploy.environment,
            squad,
            branch,
            tf_ver,
            deploy.variables,
            secreto,
            deploy.tfvar_file,
            deploy.project_path,
            current_user.username,
        )
        # Push deploy task data
        db_deploy = crud_deploys.create_new_deploy(
            db=db,
            deploy=deploy,
            stack_branch=branch,
            task_id=pipeline_plan,
            action="Plan",
            squad=squad,
            user_id=current_user.id,
            username=current_user.username,
        )
        # Push task data
        db_task = crud_tasks.create_task(
            db=db,
            task_id=pipeline_plan,
            task_name=f"{deploy.stack_name}-{squad}-{deploy.environment}-{deploy.name}",
            user_id=current_user.id,
            deploy_id=db_deploy.id,
            username=current_user.username,
            squad=squad,
            action="Plan",
        )
        return {"task": pipeline_plan}
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"{err}")


@router.patch("/{plan_id}", status_code=202)
async def update_plan_by_id(
    plan_id: int,
    background_tasks: BackgroundTasks,
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
    secreto = check_prefix(
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
        # if not "Plan" in deploy_data.action:
        #    raise ValueError("The id does not correspond to a Plan")
        # check crontime
        check_cron_schedule(deploy_update.start_time)
        check_cron_schedule(deploy_update.destroy_time)
        # Check deploy state
        if not check_deploy_state(deploy_data.task_id):
            raise ValueError("Deploy state running, cannot upgrade")
        # push task Deploy to queue and return task_id
        pipeline_plan = async_plan(
            git_repo,
            name,
            stack_name,
            environment,
            squad,
            branch,
            tf_ver,
            deploy_update.variables,
            secreto,
            deploy_update.tfvar_file,
            deploy_update.project_path,
            current_user.username,
        )
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


@router.get("/{deploy_id}", status_code=202)
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
    secreto = check_prefix(
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
            raise ValueError("Deploy state running, cannot upgrade")
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
