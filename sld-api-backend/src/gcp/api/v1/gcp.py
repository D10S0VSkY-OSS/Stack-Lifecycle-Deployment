from fastapi import APIRouter, Depends
from src.gcp.domain.entities import gcp as schemas_gcp
from src.gcp.api.container import create,get,delete

router = APIRouter()


@router.post("/", status_code=200)
async def create_new_gcloud_profile(
    create_gcp_account: schemas_gcp.GcloudBase = Depends(create.new_gcloud_profile),
):
    return create_gcp_account


@router.get("/")
async def get_all_gcloud_accounts(
    get_gcp_account: schemas_gcp.GcloudBase = Depends(get.all_gcloud_accounts),
):
    return get_gcp_account


@router.delete("/{gcloud_account_id}")
async def delete_gcloud_account_by_id(
    get_gcp_account: schemas_gcp.GcloudBase = Depends(delete.gcloud_account_by_id),
):
    return get_gcp_account
