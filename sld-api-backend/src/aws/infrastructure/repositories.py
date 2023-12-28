import datetime
from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import desc, or_


import src.aws.infrastructure.models as models
from src.aws.domain.entities import aws as schemas_aws
from src.shared.security.vault import vault_encrypt


@vault_encrypt
def encrypt(secreto):
    try:
        return secreto
    except Exception as err:
        raise err


def create_aws_profile(db: Session, aws: schemas_aws.AwsAsumeProfile) -> schemas_aws.AwsAccountResponse:
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
        return schemas_aws.AwsAccountResponse(
            id=db_aws.id,
            squad=db_aws.squad,
            environment=db_aws.environment,
            default_region=db_aws.default_region,
            role_arn=db_aws.role_arn,
            extra_variables=db_aws.extra_variables,
        )
    except Exception as err:
        raise err


async def update_aws_profile(db: Session, aws_id: int, updated_aws: schemas_aws.AwsAsumeProfile) -> schemas_aws.AwsAccountResponse:
    db_aws = db.query(models.Aws_provider).filter(models.Aws_provider.id == aws_id).first()

    if db_aws:
        # Update only the fields that are present in the updated_aws object
        if updated_aws.access_key_id:
            db_aws.access_key_id = encrypt(updated_aws.access_key_id)
        if updated_aws.secret_access_key:
            db_aws.secret_access_key = encrypt(updated_aws.secret_access_key)
        if updated_aws.extra_variables:
            db_aws.extra_variables = {key: encrypt(val) for key, val in updated_aws.extra_variables.items()}

        # Update the remaining fields
        db_aws.environment = updated_aws.environment
        db_aws.default_region = updated_aws.default_region
        db_aws.role_arn = updated_aws.role_arn
        db_aws.squad = updated_aws.squad

        try:
            db.commit()
            db.refresh(db_aws)
            return schemas_aws.AwsAccountResponse(
                id=db_aws.id,
                squad=db_aws.squad,
                environment=db_aws.environment,
                default_region=db_aws.default_region,
                role_arn=db_aws.role_arn,
                extra_variables=db_aws.extra_variables,
            )
        except Exception as err:
            raise err
    else:
        # Handle the case where the specified AWS profile ID doesn't exist
        raise ValueError(f"AWS profile with id {aws_id} not found")



def get_credentials_aws_profile(db: Session, environment: str, squad: str) -> schemas_aws.AwsAccountResponseRepo:
    aws_provider_data = (
        db.query(models.Aws_provider)
        .filter(models.Aws_provider.environment == environment)
        .filter(models.Aws_provider.squad == squad)
        .first()
    )
    return schemas_aws.AwsAccountResponseRepo(
        id=aws_provider_data.id,
        squad=aws_provider_data.squad,
        environment=aws_provider_data.environment,
        access_key_id=aws_provider_data.access_key_id,
        secret_access_key=aws_provider_data.secret_access_key,
        role_arn=aws_provider_data.role_arn,
        default_region=aws_provider_data.default_region,
        extra_variables=aws_provider_data.extra_variables,
    )


def get_all_aws_profile(
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

        results = query.order_by(desc(models.Aws_provider.id)).offset(skip).limit(limit).all()

        aws_profiles = []
        for result in results:
            aws_profile = schemas_aws.AwsAccountResponse(
                id=result.id,
                squad=result.squad,
                environment=result.environment,
                default_region=result.default_region,
                role_arn=result.role_arn,
                extra_variables=result.extra_variables,
            )
            aws_profiles.append(aws_profile)
        return aws_profiles
    except Exception as err:
        raise err


def delete_aws_profile_by_id(db: Session, aws_profile_id: int):
    try:
        db.query(models.Aws_provider).filter(
            models.Aws_provider.id == aws_profile_id
        ).delete()
        db.commit()
        return {aws_profile_id: "deleted", "aws_profile_id": aws_profile_id}
    except Exception as err:
        raise err


def get_cloud_account_by_id(db: Session, provider_id: int):
    try:
        return (
            db.query(models.Aws_provider)
            .filter(models.Aws_provider.id == provider_id)
            .first()
        )
    except Exception as err:
        raise err
