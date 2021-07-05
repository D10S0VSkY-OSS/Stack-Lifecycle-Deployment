from sqlalchemy.orm import Session
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, status

from schemas import schemas
from security import deps
from security import tokens
from helpers.get_data import check_deploy_state
from helpers.get_data import deploy, deploy_squad, stack
from helpers.push_task import async_plan
from crud import deploys as crud_deploys
from crud import tasks as crud_tasks
from helpers.get_data import check_deploy_exist, check_deploy_state, check_cron_schedule


router = APIRouter()


@router.post("/", status_code=202)
async def plan_infra_by_stack_name(
        response: Response,
        background_tasks: BackgroundTasks,
        deploy: schemas.PlanCreate,
        current_user: schemas.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)):
    response.status_code = status.HTTP_202_ACCEPTED

    squad = deploy.squad
    # Get squad from current user
    if not current_user.master:
        current_squad = current_user.squad
        if current_squad != squad:
            raise HTTPException(status_code=403, detail=f"Not enough permissions in {squad}")
    # Get  credentials by providers supported
    secreto = tokens.check_prefix(
        db, stack_name=deploy.stack_name, environment=deploy.environment, squad=squad)
    # Get info from stack data
    stack_data = stack(db, stack_name=deploy.stack_name)
    branch = stack_data.branch
    git_repo = stack_data.git_repo
    tf_ver = stack_data.tf_version
    # Check if plan exist
    plan = crud_deploys.get_deploy_by_name(
        db, deploy_name=deploy.name)
    if plan:
        raise HTTPException(
            status_code=409,
            detail="Plan already exist")
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
            secreto)
        # Push deploy task data
        db_deploy = crud_deploys.create_new_deploy(
            db=db,
            deploy=deploy,
            task_id=pipeline_plan,
            action="Plan",
            squad=squad,
            user_id=current_user.id,
            username=current_user.username)
        # Push task data
        db_task = crud_tasks.create_task(
            db=db,
            task_id=pipeline_plan,
            task_name=f"{deploy.stack_name}-{squad}-{deploy.environment}-{deploy.name}",
            user_id=current_user.id,
            deploy_id=db_deploy.id,
            username=current_user.username,
            squad=squad,
            action="Plan"
        )
        return {"task": pipeline_plan}
    except Exception as err:
        raise HTTPException(
            status_code=400,
            detail=f"{err}")


@router.patch("/{plan_id}", status_code=202)
async def update_plan_by_id(
        plan_id: int,
        background_tasks: BackgroundTasks,
        deploy_update: schemas.DeployUpdate,
        response: Response,
        current_user: schemas.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)):

    response.status_code = status.HTTP_202_ACCEPTED
    # Get info from deploy data
    if current_user.master:
        deploy_data = deploy(db, deploy_id=plan_id)
        squad = deploy_data.squad
    else:
        # Get squad from current user
        squad = current_user.squad
        deploy_data = deploy_squad(db, deploy_id=plan_id, squad=squad)
    stack_name = deploy_data.stack_name
    environment = deploy_data.environment
    name = deploy_data.name
    # Get  credentials by providers supported
    secreto = tokens.check_prefix(
        db, stack_name=stack_name, environment=environment, squad=squad)
    # Get info from stack data
    stack_data = stack(db, stack_name=stack_name)
    branch = stack_data.branch
    git_repo = stack_data.git_repo
    tf_ver = stack_data.tf_version
    try:
        #if not "Plan" in deploy_data.action:
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
            secreto)
        # Push deploy task data
        if  "Plan" in deploy_data.action:
            crud_deploys.update_deploy(
                db=db,
                deploy_id=plan_id,
                task_id=pipeline_plan,
                action="Plan",
                user_id=current_user.id,
                variables=deploy_update.variables,
                start_time=deploy_update.start_time,
                destroy_time=deploy_update.destroy_time,
                username=current_user.username)
            action="Plan"
        else:
            crud_deploys.update_plan(
                db=db,deploy_id=plan_id,task_id=pipeline_plan,action="DryRun")
            action="DryRun"
        # Push task data
        db_task = crud_tasks.create_task(
            db=db,
            task_id=pipeline_plan,
            task_name=f"{stack_name}-{squad}-{environment}-{name}",
            user_id=current_user.id,
            deploy_id=plan_id,
            username=current_user.username,
            squad=squad,
            action=action)

        return {"task_id": pipeline_plan}
    except Exception as err:
        raise HTTPException(
            status_code=400,
            detail=f"{err}")


@router.get("/{deploy_id}", status_code=202)
async def get_plan_by_id_deploy(
        deploy_id: int,
        response: Response,
        current_user: schemas.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)):

    response.status_code = status.HTTP_202_ACCEPTED
    if current_user.master:
        deploy_data = deploy(db, deploy_id=deploy_id)
    else:
        squad = current_user.squad
        deploy_data = deploy_squad(db, deploy_id=deploy_id, squad=squad)
    # Get  credentials by providers supported
    secreto = tokens.check_prefix(
        db, stack_name=deploy_data.stack_name, environment=deploy_data.environment, squad=deploy_data.squad)
    # Get info from stack data
    stack_data = stack(db, stack_name=deploy_data.stack_name)
    branch = stack_data.branch
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
            secreto)
        return {"task_id": pipeline_plan}
    except Exception as err:
        raise HTTPException(
            status_code=400,
            detail=f"{err}")
