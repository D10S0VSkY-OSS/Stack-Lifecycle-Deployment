from typing import Any
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from schemas import schemas
from schemas.schemas import Token
from security import deps
from security.tokens import validate_user


router = APIRouter()


@router.post("/access-token", response_model=Token)
def login_access_token(
    user: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(deps.get_db)) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    return validate_user(db, user.username, user.password)


@router.post("/access-token-json", response_model=Token)
def login_access_token_json(
    user: schemas.UserAuthenticate,
    db: Session = Depends(deps.get_db)) -> dict:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    return validate_user(db, user.username, user.password)
