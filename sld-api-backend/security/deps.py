from typing import Generator, List, Tuple
from password_strength import PasswordPolicy
from usernames import is_safe_username

from config.api import settings
from config.database import SessionLocal
from crud import user as crud_users
from db import models
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from schemas import schemas
from security import tokens
from sqlalchemy.orm import Session

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/authenticate/access-token"
)

class PasswordValidator:
    def __init__(self) -> None:
        self._policy = PasswordPolicy.from_names(
                length=8,
                uppercase=1,
                numbers=1,
                special=1,
                nonletters=1
                )
        print("passwd validate constructor called")
        
    def validate(self, password: str) -> bool:
        if password == None or len(password) == 0:
            return False
        if len(self._policy.test(password))>0:
            return False
        return True

class UsernameValidator:
    def __init__(self) -> None:
        self._whitelist = ["admin"]
        self._black_list = ["guest", "root", "administrator"]
        self._max_length = 12
        print("username validate constructor called")

    def validate(self, username: str) -> bool:
        print(username)
        return is_safe_username(
            username,
            whitelist=self._whitelist,
            blacklist=self._black_list,
            max_length=self._max_length
            )


class UserService:
    def __init__(self):
        pass

    def validate(self, username: str, password: str) -> Tuple[str, str]:
        password_validator = PasswordValidator()
        username_validator = UsernameValidator()
        if not password_validator.validate(password):
            return (False, "pwd_weak")
        elif not username_validator.validate(username):
            return (False, "usr_invalid")
        return (True, "")

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


def validate_password(username: str, password: str):
    user_service = UserService()
    (result, aditional_info) = user_service.validate(username, password)
    if not result:
        raise HTTPException(
            status_code=400,
            detail=f"{aditional_info}",
        )
    return True
