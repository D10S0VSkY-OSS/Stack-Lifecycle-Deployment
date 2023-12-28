from pydantic import BaseModel
from typing import Optional, Dict


class StructActionsBase(BaseModel):
    name: str
    stack_name: str
    branch: str
    environment: str
    squad: str
    iac_type: Optional[str] = "terraform"
    version: str
    secreto: Dict
    variables_file: Optional[str]
    project_path: Optional[str]
    task_id: str
