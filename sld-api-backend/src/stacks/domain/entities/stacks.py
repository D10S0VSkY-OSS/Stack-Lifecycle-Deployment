from typing import List, Optional

from pydantic import BaseModel, Field, constr


class StackBase(BaseModel):
    stack_name: constr(strip_whitespace=True)
    git_repo: constr(strip_whitespace=True)
    branch: constr(strip_whitespace=True) = "master"
    squad_access: List[str] = ["*"]
    tf_version: constr(strip_whitespace=True) = "1.3.2"
    project_path: Optional[constr(strip_whitespace=True)] = Field("", example="")
    description: constr(strip_whitespace=True)

    class Config:
        """Extra configuration options"""
        anystr_strip_whitespace = True  # remove trailing whitespace


class StackCreate(StackBase):
    pass

    class Config:
        """Extra configuration options"""
        anystr_strip_whitespace = True  # remove trailing whitespace


class Stack(StackBase):
    id: int
    task_id: constr(strip_whitespace=True)
    user_id: int

    class Config:
        orm_mode = True
