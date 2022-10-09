import datetime
import imp

import src.azure.infrastructure.models as models
from src.azure.domain.entities import azure as schemas_azure
from security.vault import vault_decrypt, vault_encrypt
from sqlalchemy import exc
from sqlalchemy.orm import Session


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


def create_azure_profile(db: Session, azure: schemas_azure.AzureBase):
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
    )
    try:
        db.add(db_azure)
        db.commit()
        db.refresh(db_azure)
        return db_azure
    except exc.IntegrityError as err:
        raise ValueError(str(err.__dict__["orig"]))
    except Exception as err:
        raise err


def get_credentials_azure_profile(db: Session, environment: str, squad: str):
    get_client_id = (
        db.query(models.Azure_provider.client_id)
        .filter(models.Azure_provider.environment == environment)
        .filter(models.Azure_provider.squad == squad)
        .first()
    )
    get_client_secret = (
        db.query(models.Azure_provider.client_secret)
        .filter(models.Azure_provider.environment == environment)
        .filter(models.Azure_provider.squad == squad)
        .first()
    )
    subscription_id = (
        db.query(models.Azure_provider.subscription_id)
        .filter(models.Azure_provider.environment == environment)
        .filter(models.Azure_provider.squad == squad)
        .first()
    )
    tenant_id = (
        db.query(models.Azure_provider.tenant_id)
        .filter(models.Azure_provider.environment == environment)
        .filter(models.Azure_provider.squad == squad)
        .first()
    )
    try:
        return {
            "client_id": decrypt(get_client_id[0]),
            "client_secret": decrypt(get_client_secret[0]),
            "subscription_id": subscription_id[0],
            "tenant_id": tenant_id[0],
        }
    except Exception as err:
        raise err


def get_squad_azure_profile(db: Session, squad: str, environment: str):
    try:
        if environment != None:
            return (
                db.query(models.Azure_provider)
                .filter(models.Azure_provider.squad == squad)
                .filter(models.Azure_provider.environment == environment)
                .first()
            )
        result = []
        for i in squad:
            result.extend(
                db.query(models.Azure_provider)
                .filter(models.Azure_provider.squad == i)
                .all()
            )
        return set(result)
    except Exception as err:
        raise err


def get_all_azure_profile(db: Session):
    try:
        return db.query(models.Azure_provider).all()
    except Exception as err:
        raise err


def delete_azure_profile_by_id(db: Session, azure_profile_id: int):
    db.query(models.Azure_provider).filter(
        models.Azure_provider.id == azure_profile_id
    ).delete()
    try:
        db.commit()
        return {azure_profile_id: "deleted", "azure_profile_id": azure_profile_id}
    except Exception as err:
        raise err
