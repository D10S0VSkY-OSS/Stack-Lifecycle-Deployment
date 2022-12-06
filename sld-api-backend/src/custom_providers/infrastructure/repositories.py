import datetime

from sqlalchemy import exc
from sqlalchemy.orm import Session

import src.custom_providers.infrastructure.models as models
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


def create_custom_provider_profile(
    db: Session, squad: str, environment: str, configuration_keyfile_json: dict
):
    encrypt_keyfile_json = encrypt(str(configuration_keyfile_json))

    db_custom_provider = models.Custom_provider(
        configuration=encrypt_keyfile_json,
        environment=environment,
        created_at=datetime.datetime.now(),
        squad=squad,
    )
    try:
        db.add(db_custom_provider)
        db.commit()
        db.refresh(db_custom_provider)
        return db_custom_provider
    except exc.IntegrityError as err:
        raise ValueError(str(err.__dict__["orig"]))
    except Exception as err:
        raise err


def get_credentials_custom_provider_profile(db: Session, environment: str, squad: str):
    try:
        get_custom_provider_keyfile = (
            db.query(models.Custom_provider.configuration)
            .filter(models.Custom_provider.environment == environment)
            .filter(models.Custom_provider.squad == squad)
            .first()
        )
        return {"custom_provider_keyfile_json": decrypt(get_custom_provider_keyfile[0])}
    except Exception as err:
        raise err


def get_squad_custom_provider_profile(db: Session, squad: str, environment: str):
    try:
        if environment != None:
            return (
                db.query(models.Custom_provider)
                .filter(models.Custom_provider.squad == squad)
                .filter(models.Custom_provider.environment == environment)
                .first()
            )
        result = []
        for i in squad:
            result.extend(
                db.query(models.Custom_provider)
                .filter(models.Custom_provider.squad == i)
                .all()
            )
        return set(result)
    except Exception as err:
        raise err


def get_all_custom_profile(db: Session):
    try:
        return db.query(models.Custom_provider).all()
    except Exception as err:
        raise err


def delete_custom_profile_by_id(db: Session, custom_profile_id: int):
    try:
        db.query(models.Custom_provider).filter(
            models.Custom_provider.id == custom_profile_id
        ).delete()
        db.commit()
        return {custom_profile_id: "deleted", "custom_profile_id": custom_profile_id}
    except Exception as err:
        raise err


def get_cloud_account_by_id(db: Session, provider_id: int):
    try:
        return (
            db.query(models.Custom_provider)
            .filter(models.Custom_provider.id == provider_id)
            .first()
        )
    except Exception as err:
        raise err
