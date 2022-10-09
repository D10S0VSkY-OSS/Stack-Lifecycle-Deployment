from typing import List

from pydantic import BaseModel, constr


class StackBase(BaseModel):
    stack_name: constr(strip_whitespace=True)
    git_repo: constr(strip_whitespace=True)
    branch: constr(strip_whitespace=True) = "master"
    squad_access: List[str] = ["*"]
    tf_version: constr(strip_whitespace=True) = "1.2.3"
    description: constr(strip_whitespace=True)


class StackCreate(StackBase):
    pass


class Stack(StackBase):
    id: int
    task_id: constr(strip_whitespace=True)
    user_id: int

    class Config:
        orm_mode = True
