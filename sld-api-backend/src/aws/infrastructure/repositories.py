import datetime
from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import desc, or_


import src.aws.infrastructure.models as models
from src.aws.domain.entities import aws as schemas_aws
from src.shared.infrastructure.respository import check_deploy_in_use
from src.shared.security.vault import vault_encrypt, vault_decrypt


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


async def create_aws_profile(db: Session, aws: schemas_aws.AwsAsumeProfile) -> schemas_aws.AwsAccountResponse:
    encrypt_access_key_id = encrypt(aws.access_key_id)
    encrypt_secret_access_key = encrypt(aws.secret_access_key)
    encrypted_extra_variables = {key: encrypt(val) for key, val in aws.extra_variables.items()} if aws.extra_variables else None

    db_aws = models.Aws_provider(
        access_key_id=encrypt_access_key_id,
        secret_access_key=encrypt_secret_access_key,
        environment=aws.environment,
        default_region=aws.default_region,
        role_arn=aws.role_arn,
        extra_variables=encrypted_extra_variables,
        created_at=datetime.datetime.now(),
        squad=aws.squad,
    )
    try:
        db.add(db_aws)
        db.commit()
        db.refresh(db_aws)
        return schemas_aws.AwsAccountResponse.model_validate(obj=db_aws)
    except Exception as err:
        db.rollback()
        raise err


async def update_aws_profile(db: Session, aws_account_id: int, updated_aws: schemas_aws.AwsAccountUpdate) -> schemas_aws.AwsAccountResponse:
    db_aws = db.query(models.Aws_provider).filter(models.Aws_provider.id == aws_account_id).first()
    await check_deploy_in_use(db=db, db_provider=db_aws, cloud_provider="aws", updated=updated_aws, account_id=aws_account_id)

    if db_aws:
        if updated_aws.access_key_id:
            db_aws.access_key_id = encrypt(updated_aws.access_key_id)
        if updated_aws.secret_access_key:
            db_aws.secret_access_key = encrypt(updated_aws.secret_access_key)
        if updated_aws.extra_variables:
            current_extra_variables = db_aws.extra_variables or {}
            for key, value in current_extra_variables.items():
                current_extra_variables[key] = decrypt(value)
            current_extra_variables = {key: value for key, value in current_extra_variables.items() if key in updated_aws.extra_variables}

            for key, value in updated_aws.extra_variables.items():
                if key and value and "***" not in value:
                    current_extra_variables[key] = value
            encrypted_extra_variables = {key: encrypt(value) for key, value in current_extra_variables.items()}
            db_aws.extra_variables = encrypted_extra_variables
        db_aws.environment = updated_aws.environment
        db_aws.default_region = updated_aws.default_region
        db_aws.role_arn = updated_aws.role_arn
        db_aws.squad = updated_aws.squad
        db_aws.updated_at = datetime.datetime.now()

        try:
            db.commit()
            db.refresh(db_aws)
            return schemas_aws.AwsAccountResponse.model_validate(db_aws)
        except Exception as err:
            db.rollback()
            raise err
    else:
        raise ValueError(f"AWS profile with id {aws_account_id} not found")


async def get_credentials_aws_profile(db: Session, environment: str, squad: str) -> schemas_aws.AwsAccountResponseRepo:
    db_aws = (
        db.query(models.Aws_provider)
        .filter(models.Aws_provider.environment == environment)
        .filter(models.Aws_provider.squad == squad)
        .first()
    )
    return schemas_aws.AwsAccountResponseRepo.model_validate(obj=db_aws)


async def get_all_aws_profile(
    db: Session, filters: schemas_aws.AwsAccountFilter, skip: int = 0, limit: int = 100
) -> List[schemas_aws.AwsAccountResponse]:
    try:
        query = db.query(models.Aws_provider)

        for field, value in filters.model_dump().items():
            if value is not None:
                if field == 'squad' and isinstance(value, list):
                    or_conditions = [getattr(models.Aws_provider, field).like(f"%{v}%") for v in value]
                    query = query.filter(or_(*or_conditions))
                else:
                    query = query.filter(getattr(models.Aws_provider, field) == value)

        db_aws = query.order_by(desc(models.Aws_provider.id)).offset(skip).limit(limit).all()

        aws_profiles = []
        for result in db_aws:
            aws_profile = schemas_aws.AwsAccountResponse(
                id=result.id,
                squad=result.squad,
                environment=result.environment,
                default_region=result.default_region,
                role_arn=result.role_arn,
                extra_variables=result.extra_variables,
                created_at=result.created_at,
                updated_at=result.updated_at,
            )
            aws_profiles.append(aws_profile)
        return aws_profiles
    except Exception as err:
        raise err


async def delete_aws_profile_by_id(db: Session, aws_account_id: int) -> schemas_aws.AwsAccountResponse:
    try:
        db_aws = db.query(models.Aws_provider).filter(
            models.Aws_provider.id == aws_account_id
        ).first()
        await check_deploy_in_use(db=db, db_provider=db_aws, cloud_provider="aws", account_id=aws_account_id)
        if db_aws:
            db.delete(db_aws)
            db.commit()
            response_data = schemas_aws.AwsAccountResponse.model_validate(db_aws)
            return response_data
        else:
            raise f"AWS profile with id {aws_account_id} not found"
    except Exception as err:
        db.rollback()
        raise err
