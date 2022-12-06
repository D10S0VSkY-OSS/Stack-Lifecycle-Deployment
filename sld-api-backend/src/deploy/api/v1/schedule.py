from fastapi import APIRouter, Depends

from src.deploy.api.container.schedule import create, delete, get, update
from src.deploy.domain.entities import schedule as schemas_schedule

router = APIRouter()


@router.get("/list/", status_code=202)
async def list_schedules(
    list_schedules: schemas_schedule.ScheduleUpdate = Depends(get.list_schedules),
):
    return list_schedules


@router.get("/{deploy_id}", status_code=202)
async def get_schedule(
    get_schedule: schemas_schedule.ScheduleUpdate = Depends(get.get_schedule),
):
    return get_schedule


@router.post("/{deploy_id}", status_code=202)
async def add_schedule(
    add_schedule: schemas_schedule.ScheduleUpdate = Depends(create.add_schedule),
):
    return add_schedule


@router.delete("/{deploy_id}", status_code=202)
async def delete_schedule(
    delete_schedule: schemas_schedule.ScheduleUpdate = Depends(delete.delete_schedule),
):
    return delete_schedule


@router.patch("/{deploy_id}", status_code=202)
async def update_schedule(
    update_schedule: schemas_schedule.ScheduleUpdate = Depends(update.update_schedule),
):
    return update_schedule
