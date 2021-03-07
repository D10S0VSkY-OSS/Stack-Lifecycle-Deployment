from sqlalchemy.orm import Session
import datetime

import db.models as models
import schemas.schemas as schemas


def create_new_deploy(
        db: Session,
        deploy: schemas.DeployCreate,
        action: str,
        user_id: int,
        squad: str,
        task_id: str,
        username: str):

    db_deploy = models.Deploy(
        name=deploy.name,
        stack_name=deploy.stack_name,
        environment=deploy.environment,
        variables=deploy.variables,
        action=action,
        username=username,
        user_id=user_id,
        task_id=task_id,
        start_time=deploy.start_time,
        destroy_time=deploy.destroy_time,
        created_at=datetime.datetime.now(),
        squad=squad,
    )
    try:
        db.add(db_deploy)
        db.commit()
        db.refresh(db_deploy)
        return db_deploy
    except Exception as err:
        raise err


def update_deploy(
        db: Session,
        deploy_id: int,
        action: str,
        username: str,
        user_id: int,
        task_id: str,
        start_time: str,
        destroy_time: str,
        variables: dict):
    db_deploy = db.query(models.Deploy).filter(
        models.Deploy.id == deploy_id).first()

    db_deploy.action = action
    db_deploy.task_id = task_id
    db_deploy.username = username
    db_deploy.user_id = user_id
    db_deploy.variables = variables
    db_deploy.updated_at = datetime.datetime.now()
    check_None = ["string"]
    if db_deploy.start_time not in check_None:
        db_deploy.start_time = start_time
    if db_deploy.destroy_time not in check_None:
        db_deploy.destroy_time = destroy_time
    try:
        db.add(db_deploy)
        db.commit()
        db.refresh(db_deploy)
        return db_deploy
    except Exception as err:
        raise err


def delete_deploy_by_id(db: Session, deploy_id: int, squad: str):
    db.query(
        models.Deploy).filter(
        models.Deploy.id == deploy_id).filter(
            models.Deploy.squad == squad).delete()
    try:
        db.commit()
        return {models.Deploy.id: "deleted", "Deploy_id": deploy_id}
    except Exception as err:
        raise err


def get_deploy_by_id(db: Session, deploy_id: int):
    try:
        return db.query(models.Deploy).filter(models.Deploy.id == deploy_id).first()
    except Exception as err:
        raise err


def get_deploy_by_name(db: Session, deploy_name: str):
    try:
        return db.query(models.Deploy).filter(models.Deploy.name == deploy_name).first()
    except Exception as err:
        raise err


def get_deploy_by_id_squad(db: Session, deploy_id: int, squad: str):
    try:
        return db.query(
            models.Deploy).filter(
            models.Deploy.id == deploy_id).filter(
            models.Deploy.squad == squad).first()
    except Exception as err:
        raise err


def get_deploy_by_name_squad(db: Session, deploy_name: str, squad: str):
    try:
        return db.query(
            models.Deploy).filter(
            models.Deploy.name == deploy_name).filter(
            models.Deploy.squad == squad).first()
    except Exception as err:
        raise err


def get_all_deploys(db: Session, skip: int = 0, limit: int = 100):
    try:
        return db.query(models.Deploy).offset(skip).limit(limit).all()
    except Exception as err:
        raise err


def get_all_deploys_by_squad(db: Session, squad: str, skip: int = 0, limit: int = 100):
    try:
        return db.query(
            models.Deploy).filter(
            models.Deploy.squad == squad).offset(skip).limit(limit).all()
    except Exception as err:
        raise err
