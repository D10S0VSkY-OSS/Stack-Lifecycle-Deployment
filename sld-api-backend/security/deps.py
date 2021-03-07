from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from crud import user as crud_users
from db import models
from schemas import schemas
from security import tokens
from config.api import settings
from config.database import SessionLocal

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
        token: str = Depends(reusable_oauth2),
        db: Session = Depends(get_db)):
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


def validate_password(password: str):
    SpecialSymbol = ['$', '@', '#', '%']
    if len(password) < settings.PASSWORD_LEN:
        raise HTTPException(
            status_code=400, detail=f"Make sure your password is at lest {settings.PASSWORD_LEN} letters")
    if len(password) > 20:
        raise HTTPException(
            status_code=400, detail="length should be not be greater than 20")
    if not any(char.isdigit() for char in password):
        raise HTTPException(
            status_code=400, detail="Make sure your password has a number in it")
    if not any(char.isupper() for char in password):
        raise HTTPException(
            status_code=400, detail="Make sure your password has a capital letter in it")
    if not any(char.islower() for char in password):
        raise HTTPException(
            status_code=400, detail="Make sure your password has a lowercase letter in it")
    if not any(char in SpecialSymbol for char in password):
        raise HTTPException(
            status_code=400, detail="Make sure your password has a one of the symbols $@#% in it")
    return True
