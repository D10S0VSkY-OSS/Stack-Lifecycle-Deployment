from fastapi import APIRouter, Depends

from src.users.api.container.users import create, delete, get, update
from src.users.domain.entities.users import (
    PasswordReset,
    User,
    UserCreate,
    UserInit,
    UserUpdate,
)

router = APIRouter()


@router.post("/start", response_model=User)
async def create_init_user(
    create_init_user: UserInit = Depends(create.create_init_user),
):
    return create_init_user


@router.post("/", response_model=User)
async def create_user(create_user: UserCreate = Depends(create.create_user)):
    return create_user


@router.patch("/{user_id}", response_model=User)
async def update_user(update_user: UserUpdate = Depends(update.update_user)):
    return update_user


@router.patch("/reset/")
async def password_reset(
    reset_passwd: PasswordReset = Depends(update.password_reset),
):
    return reset_passwd


@router.get("/")
async def list_users(
    list_users: User = Depends(get.list_users),
):
    return list_users


@router.get("/{user}")
async def list_user_by_id_or_name(
    list_user_by_id: User = Depends(get.list_user_by_id_or_name),
):
    return list_user_by_id


@router.delete("/{user}")
async def delete_user_by_id_or_username(
    delete_user: User = Depends(delete.delete_user_by_id_or_username),
):
    return delete_user
