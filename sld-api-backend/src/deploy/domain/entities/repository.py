from datetime import datetime

from pydantic import BaseModel


class DeployFilter(BaseModel):
    id: str | None = None
    task_id: str | None = None
    name: str | None = None
    action: str | None = None
    stack_name: str | None = None
    stack_branch: str | None = None
    user_id: int | None = None
    username: str | None = None
    squad: str | None = None
    environment: str | None = None
    tfvar_file: str | None = None
    project_path: str | None = None


class DeployFilterResponse(BaseModel):
    id: int
    task_id: str
    name: str
    action: str
    start_time: str | None
    destroy_time: str | None
    stack_name: str
    stack_branch: str
    created_at: datetime
    updated_at: datetime | None
    user_id: int
    username: str
    squad: str
    variables: dict
    environment: str
    tfvar_file: str | None
    project_path: str | None
    icon_path: str | None
