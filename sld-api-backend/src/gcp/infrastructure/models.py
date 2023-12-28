import datetime

from config.database import Base
from sqlalchemy import Column, DateTime, Integer, String, UniqueConstraint, JSON


class Gcloud_provider(Base):
    __tablename__ = "gcloud_provider"
    id = Column(Integer, primary_key=True, index=True)
    environment = Column(String(200), nullable=False)
    squad = Column(String(200), nullable=False)
    gcloud_keyfile_json = Column(String(5000), nullable=False)
    extra_variables = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime, nullable=True)
    __table_args__ = (UniqueConstraint("squad", "environment"),)
