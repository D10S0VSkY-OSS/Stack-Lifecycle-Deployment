from sqlalchemy.orm import Session
import datetime

from security.vault import vault_encrypt, vault_decrypt
import db.models as models


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
        db: Session,
        squad: str,
        environment: str,
        gcloud_keyfile_json: dict):
    encrypt_glcoud_keyfile_json = encrypt(str(gcloud_keyfile_json))

    db_gcloud = models.Gcloud_provider(
        gcloud_keyfile_json=encrypt_glcoud_keyfile_json,
        environment=environment,
        created_at=datetime.datetime.now(),
        squad=squad)
    try:
        db.add(db_gcloud)
        db.commit()
        db.refresh(db_gcloud)
        return db_gcloud
    except Exception as err:
        raise err


def get_credentials_gcloud_profile(db: Session, environment: str, squad: str):
    try:
        get_gcloud_keyfile = db.query(models.Gcloud_provider.gcloud_keyfile_json).filter(models.Gcloud_provider.environment == environment).filter(models.Gcloud_provider.squad == squad).first()
        return {"gcloud_keyfile_json": decrypt(get_gcloud_keyfile[0])}
    except Exception as err:
        raise err


def get_squad_gcloud_profile(db: Session, squad: str):
    try:
        return db.query(models.Gcloud_provider).filter(
            models.Gcloud_provider.squad == squad).all()
    except Exception as err:
        raise err


def get_all_gcloud_profile(db: Session):
    try:
        return db.query(models.Gcloud_provider).all()
    except Exception as err:
        raise err


def delete_gcloud_profile_by_id(db: Session, gcloud_profile_id: int):
    db.query(models.Gcloud_provider).filter(
        models.Gcloud_provider.id == gcloud_profile_id).delete()
    try:
        db.commit()
        return {gcloud_profile_id: "deleted",
                "gcloud_profile_id": gcloud_profile_id}
    except Exception as err:
        raise err
