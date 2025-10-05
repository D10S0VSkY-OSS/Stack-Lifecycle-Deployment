from pydantic import BaseModel, Field, constr


class DeployBase(BaseModel):
    name: constr(strip_whitespace=True)
    stack_name: constr(strip_whitespace=True)
    stack_branch: constr(strip_whitespace=True) | None = Field("", example="")
    username: constr(strip_whitespace=True)
    squad: constr(strip_whitespace=True)
    environment: constr(strip_whitespace=True)
    variables: constr(strip_whitespace=True)


class DeployCreate(BaseModel):
    name: constr(strip_whitespace=True)
    squad: constr(strip_whitespace=True)
    stack_name: constr(strip_whitespace=True)
    stack_branch: constr(strip_whitespace=True) | None = Field("", example="")
    environment: constr(strip_whitespace=True)
    start_time: constr(strip_whitespace=True) | None = Field(None, example="30 7 * * 0-4")
    destroy_time: constr(strip_whitespace=True) | None = Field(None, example="30 18 * * 0-4")
    tfvar_file: constr(strip_whitespace=True) | None = Field("", example="terraform.tfvars")
    project_path: constr(strip_whitespace=True) | None = Field("", example="")
    variables: dict


class DeployCreateMaster(DeployCreate):
    squad: constr(strip_whitespace=True)


class DeployDeleteMaster(BaseModel):
    squad: constr(strip_whitespace=True)


class DeployUpdate(BaseModel):
    start_time: constr(strip_whitespace=True) | None = Field("")
    destroy_time: constr(strip_whitespace=True) | None = Field("")
    stack_branch: constr(strip_whitespace=True) | None = Field("", example="")
    tfvar_file: constr(strip_whitespace=True) | None = Field("", example="terraform.tfvars")
    project_path: constr(strip_whitespace=True) | None = Field("", example="")
    variables: dict


class Deploy(DeployBase):
    id: int
    task_id: constr(strip_whitespace=True)
    user_id: int

    class Config:
        from_attributes = True
