import datetime

from sqlalchemy import desc, or_
from sqlalchemy.orm import Session
from typing import List

import src.azure.infrastructure.models as models
from src.azure.domain.entities import azure as schemas_azure
from src.shared.infrastructure.respository import check_deploy_in_use
from src.shared.security.vault import vault_decrypt, vault_encrypt


@vault_encrypt
def encrypt(secreto):
    try:
        return secreto
    except Exception as err:
        raise err


@vault_decrypt
def decrypt(secreto):
    try:
        return secreto
    except Exception as err:
        raise err


async def create_azure_profile(db: Session, azure: schemas_azure.AzureBase) -> schemas_azure.AzureAccountResponse:
    encrypted_extra_variables = {key: encrypt(val) for key, val in azure.extra_variables.items()} if azure.extra_variables else None
    encrypt_client_id = encrypt(azure.client_id)
    encrypt_client_secret = encrypt(azure.client_secret)

    db_azure = models.Azure_provider(
        client_id=encrypt_client_id,
        client_secret=encrypt_client_secret,
        subscription_id=azure.subscription_id,
        environment=azure.environment,
        tenant_id=azure.tenant_id,
        created_at=datetime.datetime.now(),
        squad=azure.squad,
        extra_variables=encrypted_extra_variables,
    )

    try:
        db.add(db_azure)
        db.commit()
        db.refresh(db_azure)
        return schemas_azure.AzureAccountResponse.model_validate(obj=db_azure)
    except Exception as err:
        db.rollback()
        raise err


async def update_azure_profile(db: Session, azure_account_id: int, updated_azure: schemas_azure.AzureAccountUpdate) -> schemas_azure.AzureAccountResponse:
    db_azure = db.query(models.Azure_provider).filter(models.Azure_provider.id == azure_account_id).first()
    await check_deploy_in_use(db=db, db_provider=db_azure, cloud_provider="azure", updated=updated_azure, account_id=azure_account_id)

    if db_azure:
        if updated_azure.client_id:
            db_azure.client_id = encrypt(updated_azure.client_id)
        if updated_azure.client_secret:
            db_azure.client_secret = encrypt(updated_azure.client_secret)
        if updated_azure.extra_variables:
            current_extra_variables = db_azure.extra_variables or {}
            for key, value in current_extra_variables.items():
                current_extra_variables[key] = decrypt(value)
            current_extra_variables = {key: value for key, value in current_extra_variables.items() if key in updated_azure.extra_variables}

            for key, value in updated_azure.extra_variables.items():
                if key and value and "***" not in value:
                    current_extra_variables[key] = value
            encrypted_extra_variables = {key: encrypt(value) for key, value in current_extra_variables.items()}
            db_azure.extra_variables = encrypted_extra_variables
        db_azure.environment = updated_azure.environment
        db_azure.subscription_id = updated_azure.subscription_id
        db_azure.tenant_id = updated_azure.tenant_id
        db_azure.squad = updated_azure.squad
        db_azure.updated_at = datetime.datetime.now()

        try:
            db.commit()
            db.refresh(db_azure)
            return schemas_azure.AzureAccountResponse.model_validate(db_azure)
        except Exception as err:
            db.rollback()
            raise err
    else:
        raise ValueError(f"azure profile with id {azure_account_id} not found")


async def get_credentials_azure_profile(db: Session, environment: str, squad: str) -> schemas_azure.AzureAccountResponseRepo:
    db_azure = (
        db.query(models.Azure_provider)
        .filter(models.Azure_provider.environment == environment)
        .filter(models.Azure_provider.squad == squad)
        .first()
    )
    return schemas_azure.AzureAccountResponseRepo.model_validate(obj=db_azure)


async def get_all_azure_profile(
    db: Session, filters: schemas_azure.AzureAccountFilter, skip: int = 0, limit: int = 100
) -> List[schemas_azure.AzureAccountResponse]:
    try:
        query = db.query(models.Azure_provider)

        for field, value in filters.model_dump().items():
            if value is not None:
                if field == 'squad' and isinstance(value, list):
                    or_conditions = [getattr(models.Azure_provider, field).like(f"%{v}%") for v in value]
                    query = query.filter(or_(*or_conditions))
                else:
                    query = query.filter(getattr(models.Azure_provider, field) == value)

        db_azure = query.order_by(desc(models.Azure_provider.id)).offset(skip).limit(limit).all()

        azure_profiles = []
        for result in db_azure:
            azure_profile = schemas_azure.AzureAccountResponse(
                id=result.id,
                squad=result.squad,
                environment=result.environment,
                subscription_id=result.subscription_id,
                tenant_id=result.tenant_id,
                extra_variables=result.extra_variables,
                created_at=result.created_at,
                updated_at=result.updated_at,
            )
            azure_profiles.append(azure_profile)
        return azure_profiles
    except Exception as err:
        raise err


async def delete_azure_profile_by_id(db: Session, azure_account_id: int) -> schemas_azure.AzureAccountResponse:
    try:
        db_azure = db.query(models.Azure_provider).filter(
            models.Azure_provider.id == azure_account_id
        ).first()
        await check_deploy_in_use(db=db, db_provider=db_azure, cloud_provider="azure", account_id=azure_account_id)
        if db_azure:
            db.delete(db_azure)
            db.commit()
            response_data = schemas_azure.AzureAccountResponse.model_validate(db_azure)
            return response_data
        else:
            raise f"Azure profile with id {azure_account_id} not found"
    except Exception as err:
        db.rollback()
        raise err
