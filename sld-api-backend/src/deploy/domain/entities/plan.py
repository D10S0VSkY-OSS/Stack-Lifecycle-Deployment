from typing import Optional

from pydantic import BaseModel, Field, constr


class PlanCreate(BaseModel):
    name: constr(strip_whitespace=True)
    stack_name: constr(strip_whitespace=True)
    stack_branch: Optional[constr(strip_whitespace=True)] = Field("", example="")
    squad: constr(strip_whitespace=True)
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
