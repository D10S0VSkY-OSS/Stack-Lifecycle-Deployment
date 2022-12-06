from fastapi import APIRouter, Depends

from src.deploy.api.container.plan import create, get, update
from src.deploy.domain.entities import plan as schemas_plan

router = APIRouter()


@router.post("/", status_code=202)
async def plan_infra_by_stack_name(
    create_plan: schemas_plan.PlanCreate = Depends(create.plan_infra_by_stack_name),
):
    return create_plan


@router.patch("/{plan_id}", status_code=202)
async def update_plan_by_id(
    update_plan: schemas_plan.PlanCreate = Depends(update.update_plan_by_id),
):
    return update_plan


@router.get("/{deploy_id}", status_code=202)
async def get_plan_by_id_deploy(
    get_plan: schemas_plan.PlanCreate = Depends(get.get_plan_by_id_deploy),
):
    return get_plan
