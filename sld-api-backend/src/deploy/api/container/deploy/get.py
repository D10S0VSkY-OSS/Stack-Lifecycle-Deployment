import requests
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from src.deploy.infrastructure import repositories as crud_deploys
from src.shared.helpers.get_data import check_squad_user, deploy, deploy_squad
from src.shared.security import deps
from src.users.domain.entities import users as schemas_users
from src.users.infrastructure import repositories as crud_users
from typing import List
from src.deploy.domain.entities.repository import DeployFilter, DeployFilterResponse
from src.deploy.domain.entities.metrics import AllMetricsResponse
from src.deploy.infrastructure.repositories import MetricsFetcher
from config.api import settings


async def get_all_deploys(
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    filters: DeployFilter = Depends(DeployFilter),
) -> List[DeployFilterResponse]:
    try:
        if not crud_users.is_master(db, current_user):
            filters.squad = current_user.squad

        return crud_deploys.get_deploys(db=db, filters=filters, skip=skip, limit=limit)
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))


async def get_deploy_by_id(
    deploy_id: int,
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):

    result = crud_deploys.get_deploy_by_id(db=db, deploy_id=deploy_id)
    if not crud_users.is_master(db, current_user):
        if not check_squad_user(current_user.squad, [result.squad]):
            raise HTTPException(
                status_code=403, detail=f"Not enough permissions in {result.squad}"
            )
    try:
        if result is None:
            raise HTTPException(status_code=404, detail="Deploy id Not Found")
        return result
    except Exception as err:
        raise HTTPException(status_code=404, detail=f"{err}")


async def get_show(
    deploy_id: int,
    db: Session = Depends(deps.get_db),
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
):
    # Get info from deploy data
    if crud_users.is_master(db, current_user):
        deploy_data = deploy(db, deploy_id=deploy_id)
    else:
        # Get squad from current user
        squad = current_user.squad
        deploy_data = deploy_squad(db, deploy_id=deploy_id, squad=squad)
    get_path = f"{deploy_data.stack_name}-{deploy_data.squad}-{deploy_data.environment}-{deploy_data.name}"
    response = requests.get(
        f"{settings.REMOTE_STATE}/terraform_state/{get_path}"
    )
    result = response.json()
    if not result:
        raise HTTPException(
            status_code=404, detail=f"Not enough output in {deploy_data.name}"
        )
    return result


async def get_output(
    deploy_id: int,
    db: Session = Depends(deps.get_db),
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
):
    if crud_users.is_master(db, current_user):
        deploy_data = deploy(db, deploy_id=deploy_id)
    else:
        # Get squad from current user
        squad = current_user.squad
        deploy_data = deploy_squad(db, deploy_id=deploy_id, squad=squad)
    get_path = f"{deploy_data.stack_name}-{deploy_data.squad}-{deploy_data.environment}-{deploy_data.name}"
    response = requests.get(
        f"{settings.REMOTE_STATE}/terraform_state/{get_path}"
    )
    json_data = response.json()
    result = json_data.get("outputs")
    if not result:
        raise HTTPException(
            status_code=404, detail=f"Not enough output in {deploy_data.name}"
        )
    return result


async def unlock_deploy(
    deploy_id: int,
    db: Session = Depends(deps.get_db),
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
):
    # Get info from deploy data
    deploy_data = deploy(db, deploy_id=deploy_id)
    squad = deploy_data.squad
    if not crud_users.is_master(db, current_user):
        if not check_squad_user(current_user.squad, [squad]):
            raise HTTPException(
                status_code=403, detail=f"Not enough permissions in {squad}"
            )
    try:
        get_path = f"{deploy_data.stack_name}-{deploy_data.squad}-{deploy_data.environment}-{deploy_data.name}"
        response = requests.delete(
            f"{settings.REMOTE_STATE}/terraform_lock/{get_path}", json={}
        )
        return response.json()
    except Exception as err:
        raise err
    

async def lock_deploy(
    deploy_id: int,
    db: Session = Depends(deps.get_db),
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
):
    # Get info from deploy data
    deploy_data = deploy(db, deploy_id=deploy_id)
    squad = deploy_data.squad
    if not crud_users.is_master(db, current_user):
        if not check_squad_user(current_user.squad, [squad]):
            raise HTTPException(
                status_code=403, detail=f"Not enough permissions in {squad}"
            )
    try:
        get_path = f"{deploy_data.stack_name}-{deploy_data.squad}-{deploy_data.environment}-{deploy_data.name}"
        response = requests.put(
            f"{settings.REMOTE_STATE}/terraform_lock/{get_path}", json={}
        )
        return response.json()
    except Exception as err:
        raise err


async def get_all_metrics(
        db: Session = Depends(deps.get_db),
        _current_user: schemas_users.User = Depends(deps.get_current_active_user),
) -> AllMetricsResponse:
    metrics_fetcher = MetricsFetcher(db)
    user_activity = metrics_fetcher.get_deploy_count_by_user()
    action_count = metrics_fetcher.get_deploy_count_by_action()
    environment_count = metrics_fetcher.get_deploy_count_by_environment()
    stack_usage = metrics_fetcher.get_deploy_count_by_stack_name()
    monthly_deploy_count = metrics_fetcher.get_monthly_deploy_count()
    squad_deploy_count = metrics_fetcher.get_deploy_count_by_squad()
    cloud_provider_usage = metrics_fetcher.get_cloud_provider_usage()
    squad_environment_usage = metrics_fetcher.get_squad_environment_usage()

    return AllMetricsResponse(
        user_activity=user_activity,
        action_count=action_count,
        environment_count=environment_count,
        stack_usage=stack_usage,
        monthly_deploy_count=monthly_deploy_count,
        squad_deploy_count=squad_deploy_count,
        cloud_provider_usage=cloud_provider_usage,
        squad_environment_usage=squad_environment_usage,
    )
