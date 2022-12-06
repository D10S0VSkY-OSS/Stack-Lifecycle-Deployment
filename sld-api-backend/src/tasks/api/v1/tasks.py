from fastapi import APIRouter, Depends

from src.tasks.api.container import delete, get

router = APIRouter()


@router.delete("/id/{task_id}")
async def get_task_by_id(
    delete_task: delete.get_task_by_id = Depends(delete.get_task_by_id),
):
    return delete_task


@router.get("/id/{task_id}")
async def get_task_by_id(
    get_task: get.get_task_by_id = Depends(get.get_task_by_id),
):
    return get_task


@router.get("/all")
async def get_all_tasks(
    get_all_tasks: get.get_all_tasks = Depends(get.get_all_tasks),
):
    return get_all_tasks


@router.get("/deploy_id/{id}")
async def get_task_by_deploy_id(
    get_task_by_deploy: get.get_task_by_deploy_id = Depends(get.get_task_by_deploy_id),
):
    return get_task_by_deploy
