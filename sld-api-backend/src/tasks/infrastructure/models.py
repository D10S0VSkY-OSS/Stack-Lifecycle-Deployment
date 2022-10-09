import datetime

from config.database import Base
from sqlalchemy import Column, DateTime, Integer, String


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
