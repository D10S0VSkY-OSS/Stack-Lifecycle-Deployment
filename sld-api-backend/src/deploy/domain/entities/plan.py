from pydantic import BaseModel, Field, constr


class PlanCreate(BaseModel):
    name: constr(strip_whitespace=True)
    stack_name: constr(strip_whitespace=True)
    stack_branch: constr(strip_whitespace=True) | None = Field("", example="")
    squad: constr(strip_whitespace=True)
    environment: constr(strip_whitespace=True)
    start_time: constr(strip_whitespace=True) | None = Field(None, example="30 7 * * 0-4")
    destroy_time: constr(strip_whitespace=True) | None = Field(None, example="30 18 * * 0-4")
    tfvar_file: constr(strip_whitespace=True) | None = Field("", example="terraform.tfvars")
    project_path: constr(strip_whitespace=True) | None = Field("", example="")
    variables: dict
