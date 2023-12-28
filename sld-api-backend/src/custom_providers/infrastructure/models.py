import datetime

from config.database import Base
from sqlalchemy import JSON, Column, DateTime, Integer, String, UniqueConstraint


class Custom_provider(Base):
    __tablename__ = "custom_provider"
    id = Column(Integer, primary_key=True, index=True)
    environment = Column(String(200), nullable=False)
    squad = Column(String(200), nullable=False)
    configuration = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime, nullable=True)
    __table_args__ = (UniqueConstraint("squad", "environment"),)
