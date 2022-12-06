from datetime import datetime, timedelta
from typing import Any, Union

from config.api import settings
from fastapi import HTTPException
from jose import jwt
from passlib.context import CryptContext

# Check bug conflict with openapi
# class TokenDecode:
#    def __init__(self, token):
#        self.token = token
#
#    def decode_access_token(self):
#        return jwt.decode(self.token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)


def decode_access_token(*, data: str):
    token = data
    return jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)


class TokenCreate:
    def __init__(self, subject: Union[str, Any], expires_delta: timedelta = None):
        self.subject = subject
        self.expires_delta = expires_delta

    def create_access_token(self) -> str:
        if self.expires_delta:
            expire = datetime.utcnow() + self.expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        to_encode = {"exp": expire, "sub": str(self.subject)}
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt


class CheckPasswd:
    def __init__(self, plain_passwd: str, hashed_password):
        self.plain_passwd = plain_passwd
        self.hashed_password = hashed_password

    def verify_password(self) -> bool:
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(self.plain_passwd, self.hashed_password)


class UserExist:
    def __init__(
        self,
        user_db,
        user: str,
        plain_passwd: str,
        check_password=CheckPasswd,
        token=TokenCreate,
    ):
        self.user_db = user_db
        self.user = user
        self.plain_passwd = plain_passwd
        self.check_password = check_password
        self.token = token

    def validate_user(self):
        try:
            # Get user info
            user = self.user_db
            # Get passwd hash
            hash_passwd = user.password
            # Pass param for check passwd
            config_check_password = self.check_password(self.plain_passwd, hash_passwd)

            # Set token time expire form global config
            access_token_expires = timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
            config_token = self.token(user.id, expires_delta=access_token_expires)

        except Exception:
            pass
        if not user:
            raise HTTPException(
                status_code=404, detail="Incorrect username or password"
            )
        elif not config_check_password.verify_password():
            raise HTTPException(
                status_code=403, detail="Incorrect username or password"
            )
        elif not user.is_active:
            raise HTTPException(status_code=403, detail="Inactive user")
        return {
            "access_token": config_token.create_access_token(),
            "token_type": "bearer",
        }
