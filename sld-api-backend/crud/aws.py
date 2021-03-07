from sqlalchemy.orm import Session
import datetime

from security.vault import vault_encrypt, vault_decrypt
import db.models as models
import schemas.schemas as schemas


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


def create_aws_profile(db: Session, aws: schemas.AwsAsumeProfile):
    encrypt_access_key_id = encrypt(aws.access_key_id)
    encrypt_secret_access_key = encrypt(aws.secret_access_key)
    db_aws = models.Aws_provider(access_key_id=encrypt_access_key_id,
                                 secret_access_key=encrypt_secret_access_key,
                                 environment=aws.environment,
                                 default_region=aws.default_region,
                                 profile_name=aws.profile_name,
                                 role_arn=aws.role_arn,
                                 source_profile=aws.source_profile,
                                 created_at=datetime.datetime.now(),
                                 squad=aws.squad)
    check_None = [None, "string"]
    if db_aws.role_arn in check_None:
        db_aws.role_arn = ""
    if db_aws.profile_name in check_None:
        db_aws.profile_name = ""
    if db_aws.source_profile in check_None:
        db_aws.source_profile = ""
    try:
        db.add(db_aws)
        db.commit()
        db.refresh(db_aws)
        return db_aws
    except Exception as err:
        raise err


def get_credentials_aws_profile(db: Session, environment: str, squad: str):
    get_access_key = db.query(models.Aws_provider.access_key_id).filter(models.Aws_provider.environment == environment).filter(models.Aws_provider.squad == squad).first()
    get_secret_access_key = db.query(models.Aws_provider.secret_access_key).filter(models.Aws_provider.environment == environment).filter(models.Aws_provider.squad == squad).first()
    default_region = db.query(models.Aws_provider.default_region).filter(models.Aws_provider.environment == environment).filter(models.Aws_provider.squad == squad).first()
    profile_name = db.query(models.Aws_provider.profile_name).filter(models.Aws_provider.environment == environment).filter(models.Aws_provider.squad == squad).first()
    role_arn = db.query(models.Aws_provider.role_arn).filter(models.Aws_provider.environment == environment).filter(models.Aws_provider.squad == squad).first()
    source_profile = db.query(models.Aws_provider.source_profile).filter(models.Aws_provider.environment == environment).filter(models.Aws_provider.squad == squad).first()
    try:
        return {
            "access_key": decrypt(get_access_key[0]),
            "secret_access_key": decrypt(get_secret_access_key[0]),
            "default_region": default_region[0],
            "profile_name": profile_name[0],
            "role_arn": role_arn[0],
            "source_profile": source_profile[0]
        }
    except Exception as err:
        raise err


def get_squad_aws_profile(db: Session, squad: str):
    try:
        return db.query(models.Aws_provider).filter(
            models.Aws_provider.squad == squad).all()
    except Exception as err:
        raise err


def get_all_aws_profile(db: Session):
    try:
        return db.query(models.Aws_provider).all()
    except Exception as err:
        raise err


def delete_aws_profile_by_id(db: Session, aws_profile_id: int):
    db.query(models.Aws_provider).filter(
        models.Aws_provider.id == aws_profile_id).delete()
    try:
        db.commit()
        return {aws_profile_id: "deleted", "aws_profile_id": aws_profile_id}
    except Exception as err:
        raise err
