# -*- encoding: utf-8 -*-

import datetime

from app import db, login_manager
from flask_login import UserMixin
from passlib.context import CryptContext
from sqlalchemy import JSON

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, index=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    fullname = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(JSON, nullable=False)
    squad = db.Column(JSON, nullable=False)
    is_active = db.Column(db.Boolean(), default=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime)
    stacks = db.relationship("Stack", back_populates="owner")

    def verify_password(self, password):
        return pwd_context.verify(password, self.password)

    @property
    def passwd(self):
        pass

    @passwd.setter
    def passwd(self, value):
        self.password = pwd_context.hash(value)
        return self.password

    def __str__(self):
        return self.username

    @classmethod
    def create_element(cls, username, password, email):
        user = User(username=username, password=password, email=email)
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def get_by_username(cls, username):
        return User.query.filter_by(username=username).first()

    @classmethod
    def get_by_email(cls, email):
        return User.query.filter_by(email=email).first()

    @classmethod
    def get_by_id(cls, id):
        return User.query.filter_by(id=id).first()


@login_manager.user_loader
def user_loader(id):
    return User.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    username = request.form.get("username")
    user = User.query.filter_by(username=username).first()
    return user if user else None


class Stack(db.Model):
    __tablename__ = "stacks"
    id = db.Column(db.Integer, primary_key=True, index=True)
    stack_name = db.Column(db.String(100), unique=True)
    git_repo = db.Column(db.String(200))
    branch = db.Column(db.String(200))
    task_id = db.Column(db.String(200))
    var_json = db.Column(db.JSON)
    var_list = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    description = db.Column(db.Text())
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    owner = db.relationship("User", back_populates="stacks")

    @property
    def little_description(self):
        if len(self.description) > 25:
            return self.description[0:24] + "..."
        return self.description

    @classmethod
    def create_element(cls, name, git, description, user_id):
        stack = Stack(name=name, git=git, description=description, user_id=user_id)

        db.session.add(stack)
        db.session.commit()

        return stack

    @classmethod
    def get_by_id(cls, id):
        return Stack.query.filter_by(id=id).first()

    @classmethod
    def update_element(cls, id, name, git, description):
        stack = Stack.get_by_id(id)

        if stack is None:
            return False

        stack.name = name
        stack.git = git
        stack.description = description

        db.session.add(stack)
        db.session.commit()

        return stack

    @classmethod
    def delete_element(cls, id):
        stack = Stack.get_by_id(id)

        if stack is None:
            return False

        db.session.delete(stack)
        db.session.commit()

        return True


class Aws_provider(db.Model):
    __tablename__ = "aws_provider"
    id = db.Column(db.Integer, primary_key=True, index=True)
    environment = db.Column(db.String(200), nullable=False)
    squad = db.Column(db.String(200), nullable=False)
    access_key_id = db.Column(db.String(200), nullable=False)
    secret_access_key = db.Column(db.String(200), nullable=False)
    default_region = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    __table_args__ = (db.UniqueConstraint("squad", "environment"),)


class Gcloud_provider(db.Model):
    __tablename__ = "gcloud_provider"
    id = db.Column(db.Integer, primary_key=True, index=True)
    environment = db.Column(db.String(200), nullable=False)
    squad = db.Column(db.String(200), nullable=False)
    gcloud_keyfile_json = db.Column(db.String(5000), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    __table_args__ = (db.UniqueConstraint("squad", "environment"),)


class Azure_provider(db.Model):
    __tablename__ = "azure_provider"
    id = db.Column(db.Integer, primary_key=True, index=True)
    environment = db.Column(db.String(200), nullable=False)
    squad = db.Column(db.String(200), nullable=False)
    client_id = db.Column(db.String(200), nullable=False)
    client_secret = db.Column(db.String(200), nullable=False)
    subscription_id = db.Column(db.String(200), nullable=False)
    tenant_id = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    __table_args__ = (db.UniqueConstraint("squad", "environment"),)


class Deploy(db.Model):
    __tablename__ = "deploy"
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(100))
    action = db.Column(db.String(100))
    stack_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    user_id = db.Column(db.Integer)
    username = db.Column(db.String(50), nullable=False)
    squad = db.Column(db.String(50), nullable=False)
    variables = db.Column(db.JSON)
    environment = db.Column(db.String(50))
    __table_args__ = (
        db.UniqueConstraint("squad", "environment", "name", "stack_name"),
    )


class Tasks(db.Model):
    __tablename__ = "tasks"
    task_id = db.Column(db.String(36), primary_key=True)
    task_name = db.Column(db.String(100))
    user_id = db.Column(db.Integer)
    deploy_id = db.Column(db.Integer)
    username = db.Column(db.String(50), nullable=False)
    squad = db.Column(JSON, nullable=False)
    action = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
