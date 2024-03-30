import datetime

from config.database import Base
from sqlalchemy import Column, DateTime, Integer, String, Text, LargeBinary


class Tasks(Base):
    __tablename__ = "tasks"
    task_id = Column(String(300), primary_key=True)
    task_name = Column(String(100))
    user_id = Column(Integer)
    deploy_id = Column(Integer)
    username = Column(String(50), nullable=False)
    squad = Column(String(50), nullable=False)
    action = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now())


class CeleryTaskMeta(Base):
    __tablename__ = "celery_taskmeta"
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(155), unique=True)
    status = Column(String(50))
    result = Column(LargeBinary)
    date_done = Column(DateTime)
    traceback = Column(Text)
    name = Column(String(155))
    args = Column(LargeBinary)
    kwargs = Column(LargeBinary)
    worker = Column(String(155))
    retries = Column(Integer)
    queue = Column(String(155))