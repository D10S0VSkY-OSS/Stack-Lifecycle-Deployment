from sqlalchemy.orm import Session
from sqlalchemy import func
import datetime

import db.models as models
import schemas.schemas as schemas


def create_new_stack(
        db: Session,
        stack: schemas.StackCreate,
        user_id: int,
        task_id: str,
        var_json: str,
        var_list: str,
        squad_access: str):
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
        squad_access=squad_access,
        task_id=task_id)
    try:
        db.add(db_stack)
        db.commit()
        db.refresh(db_stack)
        return db_stack
    except Exception as err:
        raise err


def get_all_stacks_by_squad(db: Session, squad_access: str,  skip: int = 0, limit: int = 100):
    try:
        filter_all = db.query(models.Stack).filter(models.Stack.squad_access.contains("*")).offset(skip).limit(limit).all()
        filter_squad = db.query(models.Stack).filter(models.Stack.squad_access.contains(squad_access)).offset(skip).limit(limit).all()
        return filter_all + filter_squad
    except Exception as err:
        raise err


def get_all_stacks(db: Session, squad_access: str,  skip: int = 0, limit: int = 100):
    try:
        return db.query(models.Stack).offset(skip).limit(limit).all()
    except Exception as err:
        raise err


def get_stack_by_id(db: Session, stack_id: int):
    try:
        return db.query(
            models.Stack).filter(
            models.Stack.id == stack_id).first()
    except Exception as err:
        raise err


def delete_stack_by_id(db: Session, stack_id: int):
    db.query(models.Stack).filter(models.Stack.id == stack_id).delete()
    try:
        db.commit()
        return {"result": "deleted", "stack_id": stack_id}
    except Exception as err:
        raise err


def get_stack_by_name(db: Session, stack_name: str):
    try:
        return db.query(
            models.Stack).filter(
            models.Stack.stack_name == stack_name).first()
    except Exception as err:
        raise err


def delete_stack_by_name(db: Session, stack_name: str):
    db.query(models.Stack).filter(
        models.Stack.stack_name == stack_name).delete()
    try:
        db.commit()
        return {"result": "deleted", "stack_name": stack_name}
    except Exception as err:
        raise err
