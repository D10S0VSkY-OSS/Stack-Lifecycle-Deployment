from sqlalchemy.orm import Session
from sqlalchemy import func
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


def create_fe_profile(db: Session, fe: schemas.feAsumeProfile):
    encrypt_access_key_id = encrypt(fe.access_key_id)
    encrypt_secret_access_key = encrypt(fe.secret_access_key)
    db_fe = models.fe_provider(access_key_id=encrypt_access_key_id,
                                 secret_access_key=encrypt_secret_access_key,
                                 environment=fe.environment,
                                 default_region=fe.default_region,
                                 profile_name=fe.profile_name,
                                 role_arn=fe.role_arn,
                                 source_profile=fe.source_profile,
                                 created_at=datetime.datetime.now(),
                                 squad=fe.squad)
    check_None = [None, "string"]
    if db_fe.role_arn in check_None:
        db_fe.role_arn = ""
    if db_fe.profile_name in check_None:
        db_fe.profile_name = ""
    if db_fe.source_profile in check_None:
        db_fe.source_profile = ""
    try:
        db.add(db_fe)
        db.commit()
        db.refresh(db_fe)
        return db_fe
    except Exception as err:
        raise err


def get_credentials_fe_profile(db: Session, environment: str, squad: str):
    get_access_key = db.query(models.fe_provider.access_key_id).filter(
        models.fe_provider.environment == environment).filter(models.fe_provider.squad == squad).first()
    get_secret_access_key = db.query(models.fe_provider.secret_access_key).filter(
        models.fe_provider.environment == environment).filter(models.fe_provider.squad == squad).first()
    default_region = db.query(models.fe_provider.default_region).filter(
        models.fe_provider.environment == environment).filter(models.fe_provider.squad == squad).first()
    profile_name = db.query(models.fe_provider.profile_name).filter(
        models.fe_provider.environment == environment).filter(models.fe_provider.squad == squad).first()
    role_arn = db.query(models.fe_provider.role_arn).filter(
        models.fe_provider.environment == environment).filter(models.fe_provider.squad == squad).first()
    source_profile = db.query(models.fe_provider.source_profile).filter(
        models.fe_provider.environment == environment).filter(models.fe_provider.squad == squad).first()
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


def get_squad_fe_profile(db: Session, squad: str, environment: str):
    try:
        if environment != None:
            return db.query(models.fe_provider).filter(models.fe_provider.squad == squad).filter(
                    models.fe_provider.environment == environment).first()
        result = []
        for i in squad:
            result.extend(db.query(models.fe_provider).filter(models.fe_provider.squad == i).all())
        return set(result)
    except Exception as err:
        raise err


def get_all_fe_profile(db: Session):
    try:
        return db.query(models.fe_provider).all()
    except Exception as err:
        raise err


def delete_fe_profile_by_id(db: Session, fe_profile_id: int):
    db.query(models.fe_provider).filter(
        models.fe_provider.id == fe_profile_id).delete()
    try:
        db.commit()
        return {fe_profile_id: "deleted", "fe_profile_id": fe_profile_id}
    except Exception as err:
        raise err
