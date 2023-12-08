import datetime

from config.database import Base
from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)


class Deploy(Base):
    __tablename__ = "deploy"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(36))
    name = Column(String(100))
    action = Column(String(100))
    start_time = Column(String(100))
    destroy_time = Column(String(100))
    stack_name = Column(String(100), ForeignKey("stacks.stack_name"))
    stack_branch = Column(String(100))
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime)
    user_id = Column(Integer)
    username = Column(String(50), nullable=False)
    squad = Column(String(50), nullable=False)
    variables = Column(JSON)
    tags = Column(JSON)
    environment = Column(String(50))
    tfvar_file = Column(String(50))
    project_path = Column(String(500))
    __table_args__ = (UniqueConstraint("squad", "environment", "name", "stack_name"),)
