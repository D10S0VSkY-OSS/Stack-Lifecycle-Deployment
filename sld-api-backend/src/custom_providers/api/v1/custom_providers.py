from fastapi import APIRouter, Depends

from src.custom_providers.api.container import create, delete, get
from src.custom_providers.domain.entities import (
    custom_providers as schemas_custom_provider,
)

router = APIRouter()


@router.post("/", status_code=200)
async def create_custom_provider_account(
    create_custom_provider_account: schemas_custom_provider.CustomProviderBase = Depends(
        create.create_custom_provider_profile
    ),
):
    return create_custom_provider_account


@router.get("/", status_code=200, response_model=list[schemas_custom_provider.CustomProviderResponse])
async def get_all_custom_providers_accounts(
    get_custom_provider_account: schemas_custom_provider.CustomProviderBase = Depends(
        get.all_custom_providers_accounts
    ),
):
    return get_custom_provider_account


@router.delete("/{custom_provider_id}")
async def delete_custom_provider_account_by_id(
    delete_custom_provider_account: schemas_custom_provider.CustomProviderBase = Depends(
        delete.custom_provider_account_by_id
    ),
):
    return delete_custom_provider_account
