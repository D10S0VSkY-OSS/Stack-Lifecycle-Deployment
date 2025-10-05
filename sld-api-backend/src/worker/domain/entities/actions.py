from pydantic import BaseModel


class StructActionsBase(BaseModel):
    name: str
    stack_name: str
    branch: str
    environment: str
    squad: str
    iac_type: str | None = "terraform"
    version: str
    secreto: dict
    variables_file: str | None
    project_path: str | None
    task_id: str
