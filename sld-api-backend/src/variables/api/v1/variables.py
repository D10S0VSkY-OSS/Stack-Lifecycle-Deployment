from fastapi import APIRouter, Depends

from src.variables.api.container import get

router = APIRouter()


@router.get("/json")
async def get_json(
    stack_json: dict = Depends(get.get_json),
):
    return stack_json


@router.get("/list")
async def get_list(
    stack_list: list = Depends(get.get_list),
):
    return stack_list


@router.get("/deploy/{deploy_id}")
async def get_deploy_by_id(
    deploy_variables: dict = Depends(get.get_deploy_by_id),
):
    return deploy_variables
