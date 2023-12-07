from typing import Optional, Literal, Dict

from pydantic import BaseModel, Field, constr


class DeployBase(BaseModel):
    name: constr(strip_whitespace=True)
    stack_name: constr(strip_whitespace=True)
    stack_branch: Optional[constr(strip_whitespace=True)] = Field("", example="")
    username: constr(strip_whitespace=True)
    squad: constr(strip_whitespace=True)
    environment: constr(strip_whitespace=True)
    variables: constr(strip_whitespace=True)


class DeployCreate(BaseModel):
    name: constr(strip_whitespace=True)
    squad: constr(strip_whitespace=True)
    stack_name: constr(strip_whitespace=True)
    stack_branch: Optional[constr(strip_whitespace=True)] = Field("", example="")
    environment: constr(strip_whitespace=True)
    start_time: Optional[constr(strip_whitespace=True)] = Field(
        None, example="30 7 * * 0-4"
    )
    destroy_time: Optional[constr(strip_whitespace=True)] = Field(
        None, example="30 18 * * 0-4"
    )
    tfvar_file: Optional[constr(strip_whitespace=True)] = Field(
        "", example="terraform.tfvars"
    )
    project_path: Optional[constr(strip_whitespace=True)] = Field("", example="")
    variables: dict


class DeployCreateMaster(DeployCreate):
    squad: constr(strip_whitespace=True)


class DeployDeleteMaster(BaseModel):
    squad: constr(strip_whitespace=True)


class DeployUpdate(BaseModel):
    start_time: Optional[constr(strip_whitespace=True)] = Field("")
    destroy_time: Optional[constr(strip_whitespace=True)] = Field("")
    stack_branch: Optional[constr(strip_whitespace=True)] = Field("", example="")
    tfvar_file: Optional[constr(strip_whitespace=True)] = Field(
        "", example="terraform.tfvars"
    )
    project_path: Optional[constr(strip_whitespace=True)] = Field("", example="")
    variables: dict


class Deploy(DeployBase):
    id: int
    task_id: constr(strip_whitespace=True)
    user_id: int

    class Config:
        from_attributes = True
