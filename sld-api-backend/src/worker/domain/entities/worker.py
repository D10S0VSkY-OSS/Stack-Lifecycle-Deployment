from pydantic import BaseModel
from typing import Optional, Any, Dict


import logging
from typing import List, Tuple
from subprocess import Popen, PIPE


class SubprocessHandler:
    def run_command(self, command: str) -> Tuple[int, List[str]]:
        try:
            process = Popen(
                command,
                shell=True,
                stdout=PIPE,
                stderr=PIPE,
                universal_newlines=True
            )

            # Read stdout and stderr in real-time
            output_lines = []
            while True:
                line = process.stdout.readline()
                logging.info(line.rstrip('\n'))
                if not line:
                    break
                output_lines.append(line.strip())

            # Wait for the process to finish
            returncode = process.wait()
            return returncode, output_lines

        except Exception as e:
            return 1, [str(e)]


class DownloadBinaryParams(BaseModel):
    version: str
 
    # url: Optional[str]
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
    version: str
    variables: Optional[Dict[str, Any]] = {} 
    secreto: Any
    variables_file: Optional[str] = ""
    project_path: Optional[str] = ""
    user: Optional[str] = ""
    task_id: Optional[str] = ""

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
    project_path: Optional[str] = ""
    variables_file: Optional[str] = ""
    task_id: Optional[str] = ""
    subprocess_handler: Optional[Any] = SubprocessHandler()
