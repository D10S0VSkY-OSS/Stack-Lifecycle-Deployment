from fastapi import APIRouter, Depends
from typing import List

from src.deploy.api.container.deploy import create, delete, destroy, get, update
from src.deploy.domain.entities import deploy as schemas_deploy
from src.deploy.domain.entities.repository import DeployFilterResponse, DeployFilter

router = APIRouter()


@router.post("/", status_code=202)
async def deploy_infra_by_stack_name(
    create_deploy: schemas_deploy.DeployCreate = Depends(
        create.deploy_infra_by_stack_name
    ),
):
    return create_deploy


@router.patch("/{deploy_id}", status_code=202)
async def update_deploy_by_id(
    update_deploy: schemas_deploy.DeployUpdate = Depends(update.deploy_by_id),
):
    return update_deploy


@router.put("/{deploy_id}", status_code=202)
async def destroy_infra(
    destroy_deploy: schemas_deploy.DeployBase = Depends(destroy.destroy_infra),
):
    return destroy_deploy


@router.delete("/{deploy_id}")
async def delete_infra_by_id(
    delete_deploy: schemas_deploy.DeployBase = Depends(delete.delete_infra_by_id),
):
    return delete_deploy


@router.get("/", status_code=200, response_model=List[DeployFilterResponse])
async def get_all_deploys(
    get_all_deploys: DeployFilterResponse = Depends(get.get_all_deploys),
):
    return get_all_deploys


@router.get("/{deploy_id}")
async def get_deploy_by_id(
    get_deploy: schemas_deploy.DeployBase = Depends(get.get_deploy_by_id),
):
    return get_deploy


@router.get("/output/{deploy_id}", status_code=200)
async def get_output(
    get_output: schemas_deploy.DeployBase = Depends(get.get_output),
):
    return get_output


@router.delete("/unlock/{deploy_id}", status_code=200)
async def unlock_deploy(
    unlock_deploy: schemas_deploy.DeployBase = Depends(get.unlock_deploy),
):
    return unlock_deploy

@router.put("/lock/{deploy_id}", status_code=200)
async def unlock_deploy(
    lock_deploy: schemas_deploy.DeployBase = Depends(get.lock_deploy),
):
    return lock_deploy


@router.get("/show/{deploy_id}", status_code=202)
async def get_show(
    get_show: schemas_deploy.DeployBase = Depends(get.get_show),
):
    return get_show


@router.get("/metrics/all")
async def get_metrics(
    get_metrics: schemas_deploy.DeployBase = Depends(get.get_all_metrics),
):
    return get_metrics
