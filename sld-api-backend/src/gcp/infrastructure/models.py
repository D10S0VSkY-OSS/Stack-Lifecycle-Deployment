import datetime

from config.database import Base
from sqlalchemy import (Column, DateTime, Integer, String, UniqueConstraint)


class Gcloud_provider(Base):
    __tablename__ = "gcloud_provider"
    id = Column(Integer, primary_key=True, index=True)
    environment = Column(String(200), nullable=False)
    squad = Column(String(200), nullable=False)
    gcloud_keyfile_json = Column(String(5000), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now())
    __table_args__ = (UniqueConstraint("squad", "environment"),)