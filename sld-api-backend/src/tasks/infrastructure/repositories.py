import datetime

from sqlalchemy.orm import Session

import src.tasks.infrastructure.models as models


def create_task(
    db: Session,
    task_id: str,
    task_name: str,
    user_id: int,
    deploy_id: int,
    username: str,
    squad: str,
    action: str,
):
    db_task = models.Tasks(
        task_id=task_id,
        task_name=task_name,
        user_id=user_id,
        deploy_id=deploy_id,
        username=username,
        squad=squad,
        created_at=datetime.datetime.now(),
        action=action,
    )
    try:
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    except Exception as err:
        raise err


def get_all_tasks(db: Session, skip: int = 0, limit: int = 100):
    try:
        db_query = db.query(models.Tasks)

        return (
            db_query.order_by(models.Tasks.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    except Exception as err:
        raise err


def get_all_tasks_by_squad(db: Session, squad: str, skip: int = 0, limit: int = 100):
    try:
        result = []
        for i in squad:
            result.extend(
                db.query(models.Tasks)
                .filter(models.Tasks.squad == i)
                .order_by(models.Tasks.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
        return result
    except Exception as err:
        raise err


def get_tasks_by_deploy_id(db: Session, deploy_id: int):
    try:
        return db.query(models.Tasks).filter(models.Tasks.deploy_id == deploy_id).all()
    except Exception as err:
        raise err


def delete_celery_task_meta_by_task_id(db: Session, task_id: str):
    try:
        db_task_meta = db.query(models.CeleryTaskMeta).filter(models.CeleryTaskMeta.task_id == task_id).first()
        if db_task_meta is not None:
            db.delete(db_task_meta)
            db.commit()
            return True
        else:
            return False
    except Exception as err:
        raise err

