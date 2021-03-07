from datetime import datetime, timedelta
from typing import Any, Union

from jose import jwt
from passlib.context import CryptContext
from fastapi import HTTPException

from config.api import settings
from crud import user as crud_users
from crud import aws as crud_aws
from crud import gcp as crud_gcp
from crud import azure as crud_azure

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def decode_access_token(*, data: str):
    token = data
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=settings.ALGORITHM)


def validate_user(db, user: str, plain_passwd: str):
    try:
        user = crud_users.get_user_by_username(db, username=user)
        hash_passwd = user.password
    except Exception:
        pass
    if not user:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")
    elif not verify_password(plain_passwd, hash_passwd):
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")
    elif not crud_users.is_active(db, user):
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


def check_prefix(db, stack_name: str, environment: str, squad: str):
    try:
        if any(i in stack_name.lower() for i in settings.AWS_PREFIX):
            secreto = crud_aws.get_credentials_aws_profile(
                db=db, environment=environment, squad=squad)
            return secreto
        elif any(i in stack_name.lower() for i in settings.GCLOUD_PREFIX):
            secreto = crud_gcp.get_credentials_gcloud_profile(
                db=db, environment=environment, squad=squad)
            return secreto
        elif any(i in stack_name.lower() for i in settings.AZURE_PREFIX):
            secreto = crud_azure.get_credentials_azure_profile(
                db=db, environment=environment, squad=squad)
            return secreto
        else:
            raise HTTPException(
                status_code=404,
                detail=f"stack name {stack_name.lower()} no content providers support name preffix: {settings.PROVIDERS_SUPPORT} ")
    except Exception as err:
        raise HTTPException(
            status_code=400,
            detail=f"stack name {stack_name.lower()} env {environment} error {err}  ")
