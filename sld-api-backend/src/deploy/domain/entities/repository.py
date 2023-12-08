from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DeployFilter(BaseModel):
    id: Optional[str] = None
    task_id: Optional[str] = None
    name: Optional[str] = None
    action: Optional[str] = None
    stack_name: Optional[str] = None
    stack_branch: Optional[str] = None
    user_id: Optional[int] = None
    username: Optional[str] = None
    squad: Optional[str] = None
    environment: Optional[str] = None
    tfvar_file: Optional[str] = None
    project_path: Optional[str] = None


class DeployFilterResponse(BaseModel):
    id: int
    task_id: str
    name: str
    action: str
    start_time: Optional[str]
    destroy_time: Optional[str]
    stack_name: str
    stack_branch: str
    created_at: datetime
    updated_at: Optional[datetime]
    user_id: int
    username: str
    squad: str
    variables: dict
    environment: str
    tfvar_file: Optional[str]
    project_path: Optional[str]
    icon_path: Optional[str]


