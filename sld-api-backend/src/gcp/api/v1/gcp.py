from fastapi import APIRouter, Depends

from src.gcp.api.container import create, delete, get, update
from src.gcp.domain.entities import gcp as schemas_gcp

router = APIRouter()


@router.post("/", status_code=200)
async def create_new_gcp_project(
    create_gcp_account: schemas_gcp.GcloudBase = Depends(create.new_gcp_account),
):
    return create_gcp_account


@router.patch("/{gcp_account_id}", status_code=200)
async def update_gcp_project(
        update_account: schemas_gcp.GcloudResponse = Depends(
            update.update_gcp_account
        ),
):
    return update_account



@router.get("/", status_code=200, response_model=list[schemas_gcp.GcloudResponse])
async def get_all_gcp_project(
    get_gcp_account: schemas_gcp.GcloudBase = Depends(get.get_all_gcp_accounts),
):
    return get_gcp_account


@router.delete("/{gcp_account_id}")
async def delete_gcp_project_by_id(
    get_gcp_account: schemas_gcp.GcloudBase = Depends(delete.gcp_account_by_id),
):
    return get_gcp_account
