import datetime

from config.database import Base
from sqlalchemy import Column, DateTime, Integer, String, UniqueConstraint


class Azure_provider(Base):
    __tablename__ = "azure_provider"
    id = Column(Integer, primary_key=True, index=True)
    environment = Column(String(200), nullable=False)
    squad = Column(String(200), nullable=False)
    client_id = Column(String(200), nullable=False)
    client_secret = Column(String(200), nullable=False)
    subscription_id = Column(String(200), nullable=False)
    tenant_id = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now())
    __table_args__ = (UniqueConstraint("squad", "environment"),)
