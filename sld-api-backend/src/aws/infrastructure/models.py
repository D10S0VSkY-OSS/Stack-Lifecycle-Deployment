import datetime

from config.database import Base
from sqlalchemy import Column, DateTime, Integer, String, UniqueConstraint, JSON


class Aws_provider(Base):
    __tablename__ = "aws_provider"
    id = Column(Integer, primary_key=True, index=True)
    environment = Column(String(200), nullable=False)
    squad = Column(String(200), nullable=False)
    access_key_id = Column(String(200), nullable=False)
    secret_access_key = Column(String(200), nullable=False)
    default_region = Column(String(200))
    profile_name = Column(String(200), nullable=True)
    role_arn = Column(String(200), nullable=True)
    source_profile = Column(String(200), nullable=True)
    extra_variables = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime, nullable=True)
    __table_args__ = (UniqueConstraint("squad", "environment"),)
