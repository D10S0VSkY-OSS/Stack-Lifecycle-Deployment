import datetime
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_

import src.gcp.infrastructure.models as models
from src.gcp.domain.entities import gcp as schemas_gcp
from src.shared.security.vault import vault_decrypt, vault_encrypt
from src.shared.infrastructure.respository import check_deploy_in_use


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


async def create_gcloud_profile(db: Session, gcp: schemas_gcp.GcloudBase) -> schemas_gcp.GcloudResponse:
    encrypted_extra_variables = {key: encrypt(val) for key, val in gcp.extra_variables.items()} if gcp.extra_variables else None
    encrypt_glcoud_keyfile_json = encrypt(str(gcp.gcloud_keyfile_json))

    db_gcp = models.Gcloud_provider(
        squad=gcp.squad,
        environment=gcp.environment,
        gcloud_keyfile_json=encrypt_glcoud_keyfile_json,
        extra_variables=encrypted_extra_variables,
        created_at=datetime.datetime.now(),
    )
    try:
        db.add(db_gcp)
        db.commit()
        db.refresh(db_gcp)
        return schemas_gcp.GcloudResponse.model_validate(obj=db_gcp)
    except Exception as err:
        db.rollback()
        raise err


async def get_credentials_gcloud_profile(db: Session, environment: str, squad: str) -> schemas_gcp.GcloudResponseRepo:
    try:
        db_gcp = (
            db.query(models.Gcloud_provider)
            .filter(models.Gcloud_provider.environment == environment)
            .filter(models.Gcloud_provider.squad == squad)
            .first()
        )
        return schemas_gcp.GcloudResponseRepo.model_validate(obj=db_gcp)
    except Exception as err:
        raise err


async def update_gcloud_profile(db: Session, gcp_account_id: int, updated_gcp: schemas_gcp.GcloudAccountUpdate) -> schemas_gcp.GcloudResponse:
    db_gcp = db.query(models.Gcloud_provider).filter(models.Gcloud_provider.id == gcp_account_id).first()
    await check_deploy_in_use(db=db, db_provider=db_gcp, cloud_provider="gcp", updated=updated_gcp, account_id=gcp_account_id)

    if db_gcp:
        if updated_gcp.gcloud_keyfile_json:
            db_gcp.gcloud_keyfile_json = encrypt(str(updated_gcp.gcloud_keyfile_json))
        if updated_gcp.extra_variables:
            current_extra_variables = db_gcp.extra_variables or {}
            for key, value in current_extra_variables.items():
                current_extra_variables[key] = decrypt(value)
            current_extra_variables = {key: value for key, value in current_extra_variables.items() if key in updated_gcp.extra_variables}

            for key, value in updated_gcp.extra_variables.items():
                if key and value and "***" not in value:
                    current_extra_variables[key] = value
            encrypted_extra_variables = {key: encrypt(value) for key, value in current_extra_variables.items()}
            db_gcp.extra_variables = encrypted_extra_variables
        db_gcp.environment = updated_gcp.environment
        db_gcp.squad = updated_gcp.squad
        db_gcp.updated_at = datetime.datetime.now()

        try:
            db.commit()
            db.refresh(db_gcp)
            return schemas_gcp.GcloudResponse.model_validate(db_gcp)
        except Exception as err:
            db.rollback()
            raise err
    else:
        raise ValueError(f"GCP profile with id {gcp_account_id} not found")


async def get_all_gcloud_profile(
    db: Session, filters: schemas_gcp.GcloudAccountFilter, skip: int = 0, limit: int = 100
) -> List[schemas_gcp.GcloudResponse]:
    try:
        query = db.query(models.Gcloud_provider)

        for field, value in filters.model_dump().items():
            if value is not None:
                if field == 'squad' and isinstance(value, list):
                    or_conditions = [getattr(models.Gcloud_provider, field).like(f"%{v}%") for v in value]
                    query = query.filter(or_(*or_conditions))
                else:
                    query = query.filter(getattr(models.Gcloud_provider, field) == value)

        db_gcp = query.order_by(desc(models.Gcloud_provider.id)).offset(skip).limit(limit).all()

        gcp_profiles = []
        for result in db_gcp:
            gcp_profile = schemas_gcp.GcloudResponse(
                id=result.id,
                squad=result.squad,
                environment=result.environment,
                extra_variables=result.extra_variables,
                created_at=result.created_at,
                updated_at=result.updated_at,
            )
            gcp_profiles.append(gcp_profile)
        return gcp_profiles
    except Exception as err:
        raise err


async def delete_gcloud_profile_by_id(db: Session, gcp_account_id: int) -> schemas_gcp.GcloudResponse:
    try:
        db_gcp = db.query(models.Gcloud_provider).filter(
            models.Gcloud_provider.id == gcp_account_id
        ).first()
        await check_deploy_in_use(db=db, db_provider=db_gcp, cloud_provider="gcp", account_id=gcp_account_id)
        if db_gcp:
            db.delete(db_gcp)
            db.commit()
            response_data = schemas_gcp.GcloudResponse.model_validate(db_gcp)
            return response_data
        else:
            raise f"GCP profile with id {gcp_account_id} not found"
    except Exception as err:
        db.rollback()
        raise err
