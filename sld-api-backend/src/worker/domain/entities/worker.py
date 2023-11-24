from pydantic import BaseModel
from typing import Optional, Any

class DownloadBinaryParams(BaseModel):
    version: str
    #url: Optional[str]

    class Config:
        frozenset = True

class DeployParamsBase(BaseModel):
    name: str
    stack_name: str
    environment: str
    squad: str
    project_path: Optional[str] = ""

    class config:
        frozenset = True


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
    version: str
    variables: Any
    secreto: Any
    variables_file: Optional[str] = ""
    project_path: Optional[str] = ""
    user: Optional[str] = ""

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
    variables_file: Optional[str] = ""
    user: Optional[str] = ""

    class Config:
        frozenset = True

class PlanParams(ApplyParams):
    pass