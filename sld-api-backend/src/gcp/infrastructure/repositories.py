import datetime

from sqlalchemy import exc
from sqlalchemy.orm import Session

import src.gcp.infrastructure.models as models
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


def create_gcloud_profile(
    db: Session, squad: str, environment: str, gcloud_keyfile_json: dict
):
    encrypt_glcoud_keyfile_json = encrypt(str(gcloud_keyfile_json))

    db_gcloud = models.Gcloud_provider(
        gcloud_keyfile_json=encrypt_glcoud_keyfile_json,
        environment=environment,
        created_at=datetime.datetime.now(),
        squad=squad,
    )
    try:
        db.add(db_gcloud)
        db.commit()
        db.refresh(db_gcloud)
        return db_gcloud
    except exc.IntegrityError as err:
        raise ValueError(str(err.__dict__["orig"]))
    except Exception as err:
        raise err


def get_credentials_gcloud_profile(db: Session, environment: str, squad: str):
    try:
        get_gcloud_keyfile = (
            db.query(models.Gcloud_provider.gcloud_keyfile_json)
            .filter(models.Gcloud_provider.environment == environment)
            .filter(models.Gcloud_provider.squad == squad)
            .first()
        )
        return {"gcloud_keyfile_json": decrypt(get_gcloud_keyfile[0])}
    except Exception as err:
        raise err


def get_squad_gcloud_profile(db: Session, squad: str, environment: str):
    try:
        if environment != None:
            return (
                db.query(models.Gcloud_provider)
                .filter(models.Gcloud_provider.squad == squad)
                .filter(models.Gcloud_provider.environment == environment)
                .first()
            )
        result = []
        for i in squad:
            result.extend(
                db.query(models.Gcloud_provider)
                .filter(models.Gcloud_provider.squad == i)
                .all()
            )
        return set(result)
    except Exception as err:
        raise err


def get_all_gcloud_profile(db: Session):
    try:
        return db.query(models.Gcloud_provider).all()
    except Exception as err:
        raise err


def delete_gcloud_profile_by_id(db: Session, gcloud_profile_id: int):
    try:
        db.query(models.Gcloud_provider).filter(
            models.Gcloud_provider.id == gcloud_profile_id
        ).delete()
        db.commit()
        return {gcloud_profile_id: "deleted", "gcloud_profile_id": gcloud_profile_id}
    except Exception as err:
        raise err


def get_cloud_account_by_id(db: Session, provider_id: int):
    try:
        return (
            db.query(models.Gcloud_provider)
            .filter(models.Gcloud_provider.id == provider_id)
            .first()
        )
    except Exception as err:
        raise err
