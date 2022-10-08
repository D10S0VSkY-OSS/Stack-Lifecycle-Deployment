from typing import Generator

from config.api import settings
from config.database import SessionLocal
from src.users.crud import user as crud_users
from src.users.db import models
from src.users.schema import users as schemas
from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from security import tokens
from security.validator import Container
from sqlalchemy.orm import Session

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/authenticate/access-token"
)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(reusable_oauth2), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = tokens.decode_access_token(data=token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except (jwt.JWTError, ValidationError):
        raise credentials_exception
    user = crud_users.get_user_by_id(db, id=token_data.username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_active_user(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud_users.is_active(db, current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud_users.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user


@inject
def validate_password(
    username: str, password: str, user_service=Provide[Container.user_service]
):
    (result, aditional_info) = user_service.validate(username, password)
    if not result:
        raise HTTPException(
            status_code=400,
            detail=f"{aditional_info}",
        )
    return True


container = Container()
container.wire(modules=[__name__])
