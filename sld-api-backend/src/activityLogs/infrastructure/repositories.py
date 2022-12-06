import datetime

from sqlalchemy.orm import Session

import src.activityLogs.infrastructure.models as models


def create_activity_log(db: Session, username: str, squad: str, action: str):
    db_activity = models.ActivityLogs(
        username=username,
        squad=squad,
        created_at=datetime.datetime.now(),
        action=action,
    )
    try:
        db.add(db_activity)
        db.commit()
        db.refresh(db_activity)
        return db_activity
    except Exception as err:
        raise err


def get_all_activity(db: Session, skip: int = 0, limit: int = 100):
    try:
        db_query = db.query(models.ActivityLogs)
        return (
            db_query.order_by(models.ActivityLogs.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    except Exception as err:
        raise err


def get_all_activity_by_squad(db: Session, squad: str, skip: int = 0, limit: int = 100):
    try:
        from sqlalchemy import func

        result = []
        for i in squad:
            a = f'["{i}"]'
            result.extend(
                db.query(models.ActivityLogs)
                .filter(func.json_contains(models.ActivityLogs.squad, a) == 1)
                .order_by(models.ActivityLogs.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
        return set(result)
    except Exception as err:
        raise err


def get_activity_by_username(db: Session, username: int):
    try:
        return (
            db.query(models.ActivityLogs)
            .filter(models.ActivityLogs.username == username)
            .all()
        )
    except Exception as err:
        raise err


def get_activity_by_username_squad(db: Session, username: int, squad: str):
    try:
        return (
            db.query(models.ActivityLogs)
            .filter(models.ActivityLogs.username == username)
            .filter(models.ActivityLogs.squad == squad)
            .all()
        )
    except Exception as err:
        raise err
