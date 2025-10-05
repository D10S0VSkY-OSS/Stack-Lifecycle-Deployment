from typing import Any

from pydantic import BaseModel


class DownloadBinaryParams(BaseModel):
    iac_type: str
    version: str

    # url: Optional[str]
    class Config:
        frozenset = True


class DeployParamsBase(BaseModel):
    name: str
    stack_name: str
    environment: str
    squad: str
    project_path: str | None = ""

    class config:
        frozenset = True


class GetVariablesParams(DeployParamsBase):
    pass


class RemoteStateParams(DeployParamsBase):
    pass


class TfvarsParams(DeployParamsBase):
    variables: Any

    class config:
        frozenset = True


class DeployParams(BaseModel):
    git_repo: str
    name: str
    stack_name: str
    environment: str
    squad: str
    branch: str
    iac_type: str
    version: str
    variables: dict[str, Any] | None = {}
    secreto: Any
    variables_file: str | None = ""
    project_path: str | None = ""
    user: str | None = ""
    task_id: str | None = ""

    class Config:
        frozenset = True


class DownloadGitRepoParams(BaseModel):
    git_repo: str
    name: str
    stack_name: str
    environment: str
    squad: str
    branch: str
    project_path: str

    class Config:
        frozenset = True


class ApplyParams(DeployParamsBase, DownloadBinaryParams):
    branch: str
    secreto: Any
    variables_file: str | None = ""
    user: str | None = ""

    class Config:
        frozenset = True


class PlanParams(ApplyParams):
    pass


class DestroyParams(ApplyParams):
    pass


class ActionBase(BaseModel):
    name: str
    stack_name: str
    branch: str
    environment: str
    squad: str
    version: str
    secreto: dict
    project_path: str | None = ""
    variables_file: str | None = ""
    task_id: str | None = ""
