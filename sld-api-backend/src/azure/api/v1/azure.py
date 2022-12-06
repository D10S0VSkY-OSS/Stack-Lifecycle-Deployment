from fastapi import APIRouter, Depends
from src.azure.domain.entities import azure as schemas_azure
from src.azure.api.container import create,get,delete

router = APIRouter()


@router.post("/", status_code=200)
async def create_new_azure_profile(
    create_azure_account: schemas_azure.AzureBase = Depends(create.create_new_azure_profile),
):
    return create_azure_account


@router.get("/")
async def get_all_azure_accounts(
    get_azure_account: schemas_azure.AzureBase = Depends(get.get_all_azure_accounts),
):
    return get_azure_account




@router.delete("/{azure_account_id}")
async def delete_azure_account_by_id(
    delete_azure_account: schemas_azure.AzureBase = Depends(delete.azure_account_by_id),
):
    return delete_azure_account