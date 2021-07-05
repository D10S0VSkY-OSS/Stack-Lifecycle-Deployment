from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, UniqueConstraint, JSON
from config.database import Base
from sqlalchemy.orm import relationship
import datetime


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    fullname = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    privilege = Column(Boolean, unique=False)
    master = Column(Boolean, unique=False)
    is_active = Column(Boolean(), default=True)
    squad = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime)
    stacks = relationship("Stack", back_populates="owner")


class Stack(Base):
    __tablename__ = "stacks"
    id = Column(Integer, primary_key=True, index=True)
    stack_name = Column(String(50), unique=True)
    git_repo = Column(String(200))
    branch = Column(String(50))
    task_id = Column(String(200))
    var_json = Column(JSON)
    var_list = Column(JSON)
    squad_access = Column(JSON)
    tf_version = Column(String(30))
    created_at = Column(DateTime, default=datetime.datetime.now())
    description = Column(Text())
    user_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", back_populates="stacks")


class Aws_provider(Base):
    __tablename__ = "aws_provider"
    id = Column(Integer, primary_key=True, index=True)
    environment = Column(String(200), nullable=False)
    squad = Column(String(200), nullable=False)
    access_key_id = Column(String(200), nullable=False)
    secret_access_key = Column(String(200), nullable=False)
    default_region = Column(String(200))
    profile_name = Column(String(200), nullable=False)
    role_arn = Column(String(200), nullable=True)
    source_profile = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now())
    __table_args__ = (UniqueConstraint('squad', 'environment'),)


class Gcloud_provider(Base):
    __tablename__ = "gcloud_provider"
    id = Column(Integer, primary_key=True, index=True)
    environment = Column(String(200), nullable=False)
    squad = Column(String(200), nullable=False)
    gcloud_keyfile_json = Column(String(5000), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now())
    __table_args__ = (UniqueConstraint('squad', 'environment'),)


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
    __table_args__ = (UniqueConstraint('squad', 'environment'),)


class Deploy(Base):
    __tablename__ = "deploy"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(36))
    name = Column(String(100))
    action = Column(String(100))
    start_time = Column(String(100))
    destroy_time = Column(String(100))
    stack_name = Column(String(100))
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime)
    user_id = Column(Integer)
    username = Column(String(50), nullable=False)
    squad = Column(String(50), nullable=False)
    variables = Column(JSON)
    environment = Column(String(50))
    __table_args__ = (UniqueConstraint(
        'squad', 'environment', 'name', 'stack_name'),)


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


class ActivityLogs(Base):
    __tablename__ = "activity_logs"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False)
    squad = Column(String(100), nullable=False)
    action = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now())
