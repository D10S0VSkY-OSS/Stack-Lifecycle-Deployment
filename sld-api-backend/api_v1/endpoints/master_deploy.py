from sqlalchemy.orm import Session
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, status

from schemas import schemas
from crud import deploys as crud_deploy
from crud import master as crud_master
from crud import tasks as crud_tasks
from security import deps
from security import tokens
from helpers.get_data import stack, get_deploy, check_deploy_exist, check_deploy_state, check_cron_schedule
from helpers.push_task import async_deploy, async_destroy

router = APIRouter()


@router.post("/", status_code=202)
async def deploy_infra_by_stack_name(
        response: Response,
        background_tasks: BackgroundTasks,
        deploy: schemas.DeployCreateMaster,
        current_user: schemas.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)):

    if not crud_master.is_master(db, current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    response.status_code = status.HTTP_202_ACCEPTED
    # Get  credentials by providers supported
    secreto = tokens.check_prefix(
        db, stack_name=deploy.stack_name, environment=deploy.environment, squad=deploy.squad)
    # Get info from stack data
    stack_data = stack(db, stack_name=deploy.stack_name)
    branch = stack_data.branch
    git_repo = stack_data.git_repo
    tf_ver = stack_data.tf_version
    check_deploy_exist(
        db,
        deploy.name,
        deploy.squad,
        deploy.environment,
        deploy.stack_name
    )
    try:
        #check crontime
        check_cron_schedule(deploy.start_time)
        check_cron_schedule(deploy.destroy_time)
        # push task Deploy to queue and return task_id
        pipeline_deploy = async_deploy(
            git_repo,
            deploy.name,
            deploy.stack_name,
            deploy.environment,
            deploy.squad,
            branch,
            tf_ver,
            deploy.variables,
            secreto)
        # Push deploy task data
        db_deploy = crud_deploy.create_new_deploy(
            db=db,
            deploy=deploy,
            task_id=pipeline_deploy,
            action="Apply",
            squad=deploy.squad,
            user_id=current_user.id,
            username=current_user.username)
        # Push task data
        db_task = crud_tasks.create_task(
            db=db,
            task_id=pipeline_deploy,
            task_name=f"{deploy.stack_name}-{deploy.squad}-{deploy.environment}-{deploy.name}",
            user_id=current_user.id,
            deploy_id=db_deploy.id,
            username=current_user.username,
            squad=deploy.squad,
            action="Apply"
        )

        return {"task": db_task}
    except Exception as err:
        raise HTTPException(
            status_code=400,
            detail=f"{err}")


@router.patch("/{deploy_id}", status_code=202)
async def Update_infra_by_stack_name(
        deploy_id: int,
        background_tasks: BackgroundTasks,
        deploy_update: schemas.DeployUpdate,
        response: Response,
        current_user: schemas.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)):

    if not crud_master.is_master(db, current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    response.status_code = status.HTTP_202_ACCEPTED
    # Get info from deploy data
    deploy_data = get_deploy(db, deploy_id=deploy_id)
    stack_name = deploy_data.stack_name
    environment = deploy_data.environment
    name = deploy_data.name
    squad = deploy_data.squad
    task_id = deploy_data.task_id
    # Get  credentials by providers supported
    secreto = tokens.check_prefix(
        db, stack_name=stack_name, environment=environment, squad=squad)
    # Get info from stack data
    stack_data = stack(db, stack_name=stack_name)
    branch = stack_data.branch
    git_repo = stack_data.git_repo
    tf_ver = stack_data.tf_version
    try:
        #check crontime
        check_cron_schedule(deploy_update.start_time)
        check_cron_schedule(deploy_update.destroy_time)
        # Check deploy state
        if not check_deploy_state(task_id):
            raise ValueError("Deploy state running, cannot upgrade")
        # push task Deploy Update to queue and return task_id
        pipeline_deploy = async_deploy(
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
        crud_deploy.update_deploy(
            db=db,
            deploy_id=deploy_id,
            task_id=pipeline_deploy,
            action="Update",
            user_id=current_user.id,
            variables=deploy_update.variables,
            start_time=deploy_update.start_time,
            destroy_time=deploy_update.destroy_time,
            username=current_user.username)
        # Push task data
        db_task = crud_tasks.create_task(
            db=db,
            task_id=pipeline_deploy,
            task_name=f"{stack_name}-{squad}-{environment}-{name}",
            user_id=current_user.id,
            deploy_id=deploy_id,
            username=current_user.username,
            squad=squad,
            action="Update")

        return {"task": db_task}
    except Exception as err:
        raise HTTPException(
            status_code=400,
            detail=f"{err}")


@router.put("/{deploy_id}", status_code=202)
async def destroy_infra(
        deploy_id: int,
        response: Response,
        current_user: schemas.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)):

    if not crud_master.is_master(db, current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    response.status_code = status.HTTP_202_ACCEPTED
    # Get info from deploy data
    deploy_data = get_deploy(db, deploy_id=deploy_id)
    stack_name = deploy_data.stack_name
    environment = deploy_data.environment
    start_time = deploy_data.start_time
    destroy_time = deploy_data.destroy_time
    variables = deploy_data.variables
    name = deploy_data.name
    squad = deploy_data.squad
    deploy_data.task_id
    # Get  credentials by providers supported
    secreto = tokens.check_prefix(
        db, stack_name=stack_name, environment=environment, squad=squad)
    # Get info from stack data
    stack_data = stack(db, stack_name=stack_name)
    branch = stack_data.branch
    git_repo = stack_data.git_repo
    tf_ver = stack_data.tf_version
    try:
        # Check deploy state
        if not check_deploy_state(deploy_data.task_id):
            raise ValueError("Deploy state running, cannot upgrade")
        # push task destroy to queue and return task_id
        pipeline_destroy = async_destroy(
            git_repo,
            name,
            stack_name,
            environment,
            squad,
            branch,
            tf_ver,
            variables,
            secreto
        )
        # Push deploy task data
        crud_deploy.update_deploy(
            db=db,
            deploy_id=deploy_id,
            task_id=pipeline_destroy,
            action="Destroy",
            user_id=current_user.id,
            start_time=start_time,
            destroy_time=destroy_time,
            variables=variables,
            username=current_user.username)
        # Push task data
        db_task = crud_tasks.create_task(
            db=db,
            task_id=pipeline_destroy,
            task_name=f"{stack_name}-{squad}-{environment}-{name}",
            user_id=current_user.id,
            deploy_id=deploy_id,
            username=current_user.username,
            squad=squad,
            action="Destroy")

        return {"task": db_task}
    except Exception as err:
        raise HTTPException(
            status_code=400,
            detail=f"{err}")
