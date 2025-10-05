from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, constr


class StackBase(BaseModel):
    stack_name: constr(strip_whitespace=True)
    git_repo: constr(strip_whitespace=True)
    branch: constr(strip_whitespace=True) = "main"
    squad_access: list[str] = ["*"]
    iac_type: Literal["terraform", "tofu", "terragrunt"] | None = "terraform"
    tf_version: constr(strip_whitespace=True) = "1.6.5"
    tags: list[str] | None = []
    project_path: constr(strip_whitespace=True) | None = Field("", example="")
    description: constr(strip_whitespace=True)
    icon_path: constr(strip_whitespace=True) | None = Field("", example="")

    class Config:
        freeze = True
        str_strip_whitespace = True  # remove trailing whitespace


class StackCreate(StackBase):
    pass

    class Config:
        freeze = True
        str_strip_whitespace = True  # remove trailing whitespace


class StackResponse(StackBase):
    id: int
    task_id: constr(strip_whitespace=True)
    username: constr(strip_whitespace=True) | None
    created_at: datetime | None
    updated_at: datetime | None

    class Config:
        freeze = True
        str_strip_whitespace = True  # remove trailing whitespace


class Stack(StackBase):
    id: int
    task_id: constr(strip_whitespace=True)
    user_id: int

    class Config:
        freeze = True
        from_attributes = True
