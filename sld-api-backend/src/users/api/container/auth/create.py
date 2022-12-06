from typing import Any

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.shared.security import deps
from src.users.application.tokens import UserExist
from src.users.domain.entities import users as schemas_users
from src.users.infrastructure import repositories as crud_users


def login_access_token(
    user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(deps.get_db)
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user_db = crud_users.get_user_by_username(db, username=user.username)
    validate = UserExist(user_db, user.username, user.password)
    return validate.validate_user()


def login_access_token_json(
    user: schemas_users.UserAuthenticate, db: Session = Depends(deps.get_db)
) -> dict:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user_db = crud_users.get_user_by_username(db, username=user.username)
    validate = UserExist(user_db, user.username, user.password)
    return validate.validate_user()
