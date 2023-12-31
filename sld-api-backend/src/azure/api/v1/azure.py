from fastapi import APIRouter, Depends

from src.azure.api.container import create, delete, get, update
from src.azure.domain.entities import azure as schemas_azure

router = APIRouter()


@router.post("/", status_code=200)
async def create_new_azure_subscription(
    create_azure_account: schemas_azure.AzureAccountResponse = Depends(
        create.create_new_azure_profile
    ),
):
    return create_azure_account


@router.patch("/{azure_account_id}", status_code=200)
async def update_azure_subscription(
        update_account: schemas_azure.AzureAccountResponse = Depends(
            update.update_azure_account
        ),
):
    return update_account


@router.get("/", status_code=200, response_model=list[schemas_azure.AzureAccountResponse])
async def get_all_azure_subscription(
    get_azure_account: schemas_azure.AzureAccountResponse = Depends(get.get_all_azure_accounts),
):
    return get_azure_account


@router.delete("/{azure_account_id}")
async def delete_azure_subscription_by_account_id(
    delete_azure_account: schemas_azure.AzureAccountResponse = Depends(delete.azure_account_by_id),
):
    return delete_azure_account
