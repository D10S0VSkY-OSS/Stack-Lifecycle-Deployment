from typing import List, Optional, Literal

from pydantic import BaseModel, Field, constr
from datetime import datetime


class StackBase(BaseModel):
    stack_name: constr(strip_whitespace=True)
    git_repo: constr(strip_whitespace=True)
    branch: constr(strip_whitespace=True) = "main"
    squad_access: List[str] = ["*"]
    iac_type: Optional[Literal["terraform", "tofu", "terragrunt"]] = "terraform"
    tf_version: constr(strip_whitespace=True) = "1.6.5"
    tags: Optional[List[str]] = []
    project_path: Optional[constr(strip_whitespace=True)] = Field("", example="")
    description: constr(strip_whitespace=True)
    icon_path: Optional[constr(strip_whitespace=True)] = Field("", example="")

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
    username: Optional[constr(strip_whitespace=True)]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

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
