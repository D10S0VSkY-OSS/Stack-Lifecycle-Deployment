from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.users.api.container.auth import create
from src.users.domain.entities import users as schemas_users

router = APIRouter()


@router.post("/access-token", response_model=schemas_users.Token)
def login_access_token(
    user_token: OAuth2PasswordRequestForm = Depends(create.login_access_token),
) -> schemas_users.Token:
    return user_token


@router.post("/access-token-json", response_model=schemas_users.Token)
def login_access_token_json(
    user_token: schemas_users.UserAuthenticate = Depends(
        create.login_access_token_json
    ),
) -> schemas_users.Token:
    return user_token
