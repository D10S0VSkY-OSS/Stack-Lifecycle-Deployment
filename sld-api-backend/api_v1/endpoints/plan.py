from sqlalchemy.orm import Session
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, status

from schemas import schemas
from security import deps
from security import tokens
from helpers.get_data import check_deploy_state
from helpers.get_data import deploy, deploy_squad, stack
from helpers.push_task import async_plan


router = APIRouter()


@router.post("/plan", status_code=202)
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
        return {"task": pipeline_plan}
    except Exception as err:
        raise HTTPException(
            status_code=400,
            detail=f"{err}")


@router.get("/plan/{deploy_id}", status_code=202)
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
        pipeline_plan = asyncPlan(
            git_repo,
            deploy_data.name,
            deploy_data.stack_name,
            deploy_data.environment,
            deploy_data.squad,
            branch,
            tf_ver,
            deploy_data.variables,
            secreto)
        return {"task": pipeline_plan}
    except Exception as err:
        raise HTTPException(
            status_code=400,
            detail=f"{err}")
