import bcrypt
from sqlalchemy.orm import Session
import datetime

from security.vault import vault_encrypt, vault_decrypt
from security.tokens import get_password_hash
from config.api import settings
import db.models as models
import schemas.schemas as schemas


hashing_passwd = get_password_hash


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


def is_active(db: Session, user: schemas.UserCreate) -> bool:
    try:
        return user.is_active
    except Exception as err:
        raise err


def is_superuser(db: Session, user: schemas.UserCreate) -> bool:
    try:
        return user.privilege
    except Exception as err:
        raise err


def is_master(db: Session, user: schemas.UserCreate) -> bool:
    try:
        return user.master
    except Exception as err:
        raise err


def get_user_by_username(db: Session, username: str):
    try:
        return db.query(
            models.User).filter(
            models.User.username == username).first()
    except Exception as err:
        raise err


def get_user_by_id(db: Session, id: int):
    try:
        return db.query(models.User).filter(models.User.id == id).first()
    except Exception as err:
        raise err


def get_users(db: Session, skip: int = 0, limit: int = 100):
    try:
        return db.query(models.User).offset(skip).limit(limit).all()
    except Exception as err:
        raise err


def create_init_user(db: Session, password: str):
    db_user = models.User(username=settings.INIT_USER.get("username"),
                          fullname=settings.INIT_USER.get("fullname"),
                          email=settings.INIT_USER.get("email"),
                          squad="admin",
                          master=True,
                          privilege=True,
                          is_active=True,
                          created_at=datetime.datetime.now(),
                          password=hashing_passwd(password))
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as err:
        raise err


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(**user.dict())
    db_user.password = hashing_passwd(user.password)
    db_user.created_at = datetime.datetime.now()
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as err:
        raise err


def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    db_user = db.query(models.User).filter(
        models.User.id == user_id).first()
    db_user.updated_at = datetime.datetime.now()
    check_None = [None, "", "string"]
    if user.password not in check_None:
        db_user.password = hashing_passwd(user.password)
    if user.username not in check_None:
        db_user.username = user.username
    if user.email not in check_None:
        db_user.email = user.email
    if user.squad not in check_None:
        db_user.squad = user.squad
    if user.fullname not in check_None:
        db_user.fullname = user.fullname
    if user.privilege not in check_None:
        db_user.privilege = user.privilege
    if user.is_active not in check_None:
        db_user.is_active = user.is_active
    if user.master not in check_None:
        db_user.master = user.master
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as err:
        raise err


def delete_user_by_id(db: Session, id: int):
    db.query(models.User).filter(
        models.User.id == id).delete()
    try:
        db.commit()
        return {id: "deleted"}
    except Exception as err:
        raise err


def delete_user_by_name(db: Session, username: str):
    db.query(models.User).filter(
        models.User.username == username).delete()
    try:
        db.commit()
        return {username: "deleted"}
    except Exception as err:
        raise err


def check_username_password(db: Session, user: schemas.UserAuthenticate):
    db_user_info: models.User = get_user_by_username(
        db, username=user.username)
    try:
        return bcrypt.checkpw(
            user.password.encode('utf-8'),
            db_user_info.password.encode('utf-8'))
    except Exception as err:
        raise err


def create_new_stack(
        db: Session,
        stack: schemas.StackCreate,
        user_id: int,
        task_id: str,
        var_json: str,
        var_list: str):
    db_stack = models.Stack(
        stack_name=stack.stack_name,
        git_repo=stack.git_repo,
        tf_version=stack.tf_version,
        description=stack.description,
        branch=stack.branch,
        user_id=user_id,
        created_at=datetime.datetime.now(),
        var_json=var_json,
        var_list=var_list,
        task_id=task_id)
    try:
        db.add(db_stack)
        db.commit()
        db.refresh(db_stack)
        return db_stack
    except Exception as err:
        raise err


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
   # if db_deploy.start_time not in check_None:
    db_deploy.start_time = start_time
    # if db_deploy.destroy_time not in check_None:
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
        return db.query(
            models.Deploy).filter(
            models.Deploy.id == deploy_id).first()
    except Exception as err:
        raise err


def get_deploy_by_name(db: Session, deploy_name: str):
    try:
        return db.query(
            models.Deploy).filter(
            models.Deploy.name == deploy_name).first()
    except Exception as err:
        raise err


def get_all_deploys(db: Session, skip: int = 0, limit: int = 100):
    try:
        return db.query(
            models.Deploy).offset(skip).limit(limit).all()
    except Exception as err:
        raise err
