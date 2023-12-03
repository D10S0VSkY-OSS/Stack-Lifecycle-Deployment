from fastapi import APIRouter, Depends
from typing import List

from src.stacks.api.container import create, delete, get, update
from src.stacks.domain.entities import stacks as schemas_stacks

router = APIRouter()


@router.post("/", response_model=schemas_stacks.StackResponse)
def create_new_stack(
    create_stack: schemas_stacks.StackCreate = Depends(create.create_new_stack),
):
    return create_stack


@router.patch("/{stack_id}", response_model=schemas_stacks.StackResponse)
def update_stack(
    update_stack: schemas_stacks.StackCreate = Depends(update.update_stack),
):
    return update_stack


@router.get("/", response_model=List[schemas_stacks.StackResponse])
async def get_all_stacks(
    get_all_stacks: schemas_stacks.Stack = Depends(get.get_all_stacks),
):
    return get_all_stacks


@router.get("/{stack}", response_model=schemas_stacks.StackResponse)
async def get_stack_by_id_or_name(
    get_stack: schemas_stacks.Stack = Depends(get.get_stack_by_id_or_name),
):
    return get_stack


@router.delete("/{stack}")
async def delete_stack_by_id_or_name(
    delete_stack: schemas_stacks.Stack = Depends(delete.delete_stack_by_id_or_name),
):
    return delete_stack
