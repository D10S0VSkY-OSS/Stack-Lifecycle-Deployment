from sqlalchemy.orm import Session
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, status

from schemas import schemas
from crud import deploys as crud_deploys
from crud import tasks as crud_tasks
from security import deps
from security import tokens
from helpers.get_data import check_deploy_exist, check_deploy_state
from helpers.get_data import stack, deploy, deploy_squad, check_deploy_exist
from helpers.push_task import asyncDeploy, asyncDestroy
from helpers.push_task import asyncOutput, asyncUnlock, asyncScheduleDelete
from helpers.push_task import asyncShow


router = APIRouter()


@router.post("/", status_code=202)
async def deploy_infra_by_stack_name(
        response: Response,
        background_tasks: BackgroundTasks,
        deploy: schemas.DeployCreate,
        current_user: schemas.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)):

    response.status_code = status.HTTP_202_ACCEPTED
    # Get squad from current user
    squad = current_user.squad
    # Get  credentials by providers supported
    secreto = tokens.check_prefix(
        db, stack_name=deploy.stack_name, environment=deploy.environment, squad=squad)
    # Get info from stack data
    stack_data = stack(db, stack_name=deploy.stack_name)
    branch = stack_data.branch
    git_repo = stack_data.git_repo
    tf_ver = stack_data.tf_version
    check_deploy_exist(
        db,
        deploy.name,
        squad,
        deploy.environment,
        deploy.stack_name
    )
    try:
        # push task Deploy to queue and return task_id
        pipeline_deploy = asyncDeploy(
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
            task_id=pipeline_deploy,
            action="Apply",
            squad=squad,
            user_id=current_user.id,
            username=current_user.username)
        # Push task data
        db_task = crud_tasks.create_task(
            db=db,
            task_id=pipeline_deploy,
            task_name=f"{deploy.stack_name}-{squad}-{deploy.environment}-{deploy.name}",
            user_id=current_user.id,
            deploy_id=db_deploy.id,
            username=current_user.username,
            squad=squad,
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

    response.status_code = status.HTTP_202_ACCEPTED
    # Get info from deploy data
    if current_user.master:
        deploy_data = deploy(db, deploy_id=deploy_id)
        squad = deploy_data.squad
    else:
        # Get squad from current user
        squad = current_user.squad
        deploy_data = deploy_squad(db, deploy_id=deploy_id, squad=squad)
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
        # Check deploy state
        if not check_deploy_state(deploy_data.task_id):
            raise ValueError("Deploy state running, cannot upgrade")
        # push task Deploy Update to queue and return task_id
        pipeline_deploy = asyncDeploy(
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
        crud_deploys.update_deploy(
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
            task_name=f"{deploy.stack_name}-{squad}-{deploy.environment}-{deploy.name}",
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

    response.status_code = status.HTTP_202_ACCEPTED
    # Get info from deploy data
    if current_user.master:
        deploy_data = deploy(db, deploy_id=deploy_id)
        squad = deploy_data.squad
    else:
        # Get squad from current user
        squad = current_user.squad
        deploy_data = deploy_squad(db, deploy_id=deploy_id, squad=squad)
    stack_name = deploy_data.stack_name
    environment = deploy_data.environment
    start_time = deploy_data.start_time
    destroy_time = deploy_data.destroy_time
    variables = deploy_data.variables
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
        # Check deploy state
        if not check_deploy_state(deploy_data.task_id):
            raise ValueError("Deploy state running, cannot upgrade")
        # push task destroy to queue and return task_id
        pipeline_destroy = asyncDestroy(
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
        crud_deploys.update_deploy(
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


@router.get("/")
async def get_all_deploys(
        current_user: schemas.User = Depends(deps.get_current_active_user),
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(deps.get_db)):
    try:
        if current_user.master:
            return crud_deploys.get_all_deploys(db=db, skip=skip, limit=limit)
        else:
            squad = current_user.squad
            return crud_deploys.get_all_deploys_by_squad(db=db, squad=squad, skip=skip, limit=limit)
    except Exception as err:
        raise HTTPException(
            status_code=400,
            detail=f"{err}")


@router.get("/{deploy_id}")
async def get_deploy_by_id(
        deploy_id,
        current_user: schemas.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)):
    try:
        if current_user.master:
            if deploy_id.isdigit():
                result = crud_deploys.get_deploy_by_id(
                    db=db, deploy_id=deploy_id)
            else:
                result = crud_deploys.get_deploy_by_name(
                    db=db, deploy_name=deploy_id)
        else:
            squad = current_user.squad
            if deploy_id.isdigit():
                result = crud_deploys.get_deploy_by_id_squad(
                    db=db, deploy_id=deploy_id, squad=squad)
            else:
                result = crud_deploys.get_deploy_by_name_squad(
                    db=db, deploy_name=deploy_id)
        if result is None:
            raise Exception("Deploy id Not Found")
        return result
    except Exception as err:
        raise HTTPException(
            status_code=404,
            detail=f"{err}")


@router.delete("/{deploy_id}")
async def delete_infra_by_id(
        deploy_id: int,
        current_user: schemas.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)):

    # Get info from deploy data
    if current_user.master:
        deploy_data = deploy(db, deploy_id=deploy_id)
        squad = deploy_data.squad
    else:
        # Get squad from current user
        squad = current_user.squad
        deploy_data = deploy_squad(db, deploy_id=deploy_id, squad=squad)
    stack_name = deploy_data.stack_name
    environment = deploy_data.environment
    name = deploy_data.name
    variables = deploy_data.variables
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
        # Delete deploy db by id
        crud_deploys.delete_deploy_by_id(
            db=db,
            deploy_id=deploy_id,
            squad=squad
        )
        # push task destroy to queue and return task_id
        # push task destroy to queue and return task_id
        pipeline_destroy = asyncDestroy(
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
        # Push task data
        db_task = crud_tasks.create_task(
            db=db,
            task_id=pipeline_destroy,
            task_name=f"{deploy_data.stack_name}-{squad}-{deploy_data.environment}-{deploy_data.name}",
            user_id=current_user.id,
            deploy_id=deploy_id,
            username=current_user.username,
            squad=squad,
            action="Delete")
        return {"task": db_task}

    except Exception as err:
        raise HTTPException(
            status_code=400,
            detail=f"{err}")
    finally:
        _result = asyncScheduleDelete(name, squad)


@router.get("/output/{deploy_id}", status_code=200)
async def get_output(
        deploy_id: int,
        db: Session = Depends(deps.get_db),
        current_user: schemas.User = Depends(deps.get_current_active_user)):
    # Get info from deploy data
    if current_user.master:
        deploy_data = deploy(db, deploy_id=deploy_id)
        squad = deploy_data.squad
    else:
        # Get squad from current user
        squad = current_user.squad
        deploy_data = deploy_squad(db, deploy_id=deploy_id, squad=squad)
    try:
        stack_name = deploy_data.stack_name
        environment = deploy_data.environment
        name = deploy_data.name
        # Get  credentials by providers supported
        return asyncOutput(stack_name, environment, squad, name)
    except Exception as err:
        raise HTTPException(
            status_code=400,
            detail=f"{err}")


@router.put("/unlock/{deploy_id}", status_code=200)
async def unlock_deploy(
        deploy_id: int,
        db: Session = Depends(deps.get_db),
        current_user: schemas.User = Depends(deps.get_current_active_user)):
    # Get info from deploy data
    if current_user.master:
        deploy_data = deploy(db, deploy_id=deploy_id)
        squad = deploy_data.squad
    else:
        # Get squad from current user
        squad = current_user.squad
        deploy_data = deploy_squad(db, deploy_id=deploy_id, squad=squad)
    try:
        stack_name = deploy_data.stack_name
        environment = deploy_data.environment
        name = deploy_data.name
        # Get  credentials by providers supported
        return asyncUnlock(stack_name, environment, squad, name)
    except Exception as err:
        raise HTTPException(
            status_code=400,
            detail=f"{err}")


@router.get("/show/{deploy_id}", status_code=202)
async def get_show(
        deploy_id: int,
        db: Session = Depends(deps.get_db),
        current_user: schemas.User = Depends(deps.get_current_active_user)):
    # Get info from deploy data
    if current_user.master:
        deploy_data = deploy(db, deploy_id=deploy_id)
        squad = deploy_data.squad
    else:
        # Get squad from current user
        squad = current_user.squad
        deploy_data = deploy_squad(db, deploy_id=deploy_id, squad=squad)
    stack_name = deploy_data.stack_name
    environment = deploy_data.environment
    name = deploy_data.name
    try:
        return asyncShow(stack_name, environment, squad, name)
    except Exception as err:
        raise HTTPException(
            status_code=400,
            detail=f"{err}")
