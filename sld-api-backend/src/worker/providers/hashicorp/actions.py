import os
import subprocess
from dataclasses import dataclass

import jmespath
import requests
from config.api import settings

from src.worker.security.providers_credentials import secret, unsecret


@dataclass
class StructBase:
    name: str
    stack_name: str
    branch: str
    environment: str
    squad: str


@dataclass
class Actions(StructBase):
    version: str
    secreto: dict
    variables_file: str
    project_path: str
    """
    In this class are all the methods equivalent to the terraform commands
    """

    def plan_execute(self) -> dict:
        try:
            secret(
                self.stack_name, self.environment, self.squad, self.name, self.secreto
            )
            deploy_state = (
                f"{self.environment}_{self.stack_name}_{self.squad}_{self.name}"
            )
            # Execute task
            variables_files = (
                f"{self.stack_name}.tfvars.json"
                if self.variables_file == "" or self.variables_file == None
                else self.variables_file
            )

            if not self.project_path:
                os.chdir(
                    f"/tmp/{self.stack_name}/{self.environment}/{self.squad}/{self.name}"
                )
            os.chdir(
                f"/tmp/{self.stack_name}/{self.environment}/{self.squad}/{self.name}/{self.project_path}"
            )
            result = subprocess.run(
                f"/tmp/{self.version}/terraform init -input=false --upgrade",
                shell=True,
                capture_output=True,
                encoding="utf8",
            )
            result = subprocess.run(
                f"/tmp/{self.version}/terraform plan -input=false -refresh -no-color -var-file={variables_files} -out={self.stack_name}.tfplan",
                shell=True,
                capture_output=True,
                encoding="utf8",
            )
            unsecret(
                self.stack_name, self.environment, self.squad, self.name, self.secreto
            )

            # Capture events
            rc = result.returncode
            # check result
            if rc != 0:
                return {
                    "command": "plan",
                    "deploy": self.name,
                    "squad": self.squad,
                    "stack_name": self.stack_name,
                    "environment": self.environment,
                    "rc": rc,
                    "tfvars_files": self.variables_file,
                    "remote_state": f"http://remote-state:8080/terraform_state/{deploy_state}",
                    "project_path": f"/tmp/{self.stack_name}/{self.environment}/{self.squad}/{self.name}/{self.project_path}",
                    "stdout": result.stderr.split("\n"),
                }
            return {
                "command": "plan",
                "deploy": self.name,
                "squad": self.squad,
                "stack_name": self.stack_name,
                "environment": self.environment,
                "rc": rc,
                "tfvars_files": self.variables_file,
                "remote_state": f"http://remote-state:8080/terraform_state/{deploy_state}",
                "project_path": f"/tmp/{self.stack_name}/{self.environment}/{self.squad}/{self.name}/{self.project_path}",
                "stdout": result.stdout.split("\n"),
            }
        except Exception:
            return {
                "command": "plan",
                "deploy": self.name,
                "squad": self.squad,
                "stack_name": self.stack_name,
                "environment": self.environment,
                "rc": rc,
                "tfvars_files": self.variables_file,
                "remote_state": f"http://remote-state:8080/terraform_state/{deploy_state}",
                "project_path": f"/tmp/{self.stack_name}/{self.environment}/{self.squad}/{self.name}/{self.project_path}",
                "stdout": result.stderr.split("\n"),
            }

    def apply_execute(self) -> dict:
        try:
            secret(
                self.stack_name, self.environment, self.squad, self.name, self.secreto
            )
            deploy_state = (
                f"{self.environment}_{self.stack_name}_{self.squad}_{self.name}"
            )
            # Execute task

            if not self.project_path:
                os.chdir(
                    f"/tmp/{self.stack_name}/{self.environment}/{self.squad}/{self.name}"
                )
            os.chdir(
                f"/tmp/{self.stack_name}/{self.environment}/{self.squad}/{self.name}/{self.project_path}"
            )

            result = subprocess.run(
                f"/tmp/{self.version}/terraform init -input=false --upgrade",
                shell=True,
                capture_output=True,
                encoding="utf8",
            )
            result = subprocess.run(
                f"/tmp/{self.version}/terraform apply -input=false -auto-approve -no-color {self.stack_name}.tfplan",
                shell=True,
                capture_output=True,
                encoding="utf8",
            )
            unsecret(
                self.stack_name, self.environment, self.squad, self.name, self.secreto
            )

            # Capture events
            rc = result.returncode
            # check result
            if rc != 0:
                return {
                    "command": "apply",
                    "deploy": self.name,
                    "self.squad": self.squad,
                    "self.stack_name": self.stack_name,
                    "self.environment": self.environment,
                    "rc": rc,
                    "tfvars_files": self.variables_file,
                    "remote_state": f"http://remote-state:8080/terraform_state/{deploy_state}",
                    "self.project_path": f"/tmp/{self.stack_name}/{self.environment}/{self.squad}/{self.name}/{self.project_path}",
                    "stdout": result.stderr.split("\n"),
                }
            return {
                "command": "apply",
                "deploy": self.name,
                "self.squad": self.squad,
                "self.stack_name": self.stack_name,
                "self.environment": self.environment,
                "rc": rc,
                "tfvars_files": self.variables_file,
                "self.project_path": f"/tmp/{self.stack_name}/{self.environment}/{self.squad}/{self.name}/{self.project_path}",
                "remote_state": f"http://remote-state:8080/terraform_state/{deploy_state}",
                "stdout": result.stdout.split("\n"),
            }
        except Exception:
            return {
                "command": "apply",
                "deploy": self.name,
                "self.squad": self.squad,
                "self.stack_name": self.stack_name,
                "self.environment": self.environment,
                "rc": 1,
                "tfvars_files": self.variables_file,
                "self.project_path": f"/tmp/{self.stack_name}/{self.environment}/{self.squad}/{self.name}/{self.project_path}",
                "remote_state": f"http://remote-state:8080/terraform_state/{deploy_state}",
                "stdout": "ko",
            }

    def destroy_execute(self) -> dict:
        try:
            secret(
                self.stack_name, self.environment, self.squad, self.name, self.secreto
            )
            deploy_state = (
                f"{self.environment}_{self.stack_name}_{self.squad}_{self.name}"
            )
            # Execute task
            variables_files = (
                f"{self.stack_name}.tfvars.json"
                if self.variables_file == "" or self.variables_file == None
                else self.variables_file
            )
            if not self.project_path:
                os.chdir(
                    f"/tmp/{self.stack_name}/{self.environment}/{self.squad}/{self.name}"
                )
            os.chdir(
                f"/tmp/{self.stack_name}/{self.environment}/{self.squad}/{self.name}/{self.project_path}"
            )

            result = subprocess.run(
                f"/tmp/{self.version}/terraform init -input=false --upgrade",
                shell=True,
                capture_output=True,
                encoding="utf8",
            )
            result = subprocess.run(
                f"/tmp/{self.version}/terraform destroy -input=false -auto-approve -no-color -var-file={variables_files}",
                shell=True,
                capture_output=True,
                encoding="utf8",
            )
            unsecret(
                self.stack_name, self.environment, self.squad, self.name, self.secreto
            )
            # Capture events
            rc = result.returncode
            # check result
            if rc != 0:
                return {
                    "command": "destroy",
                    "deploy": self.name,
                    "self.squad": self.squad,
                    "self.stack_name": self.stack_name,
                    "self.environment": self.environment,
                    "rc": rc,
                    "tfvars_files": self.variables_file,
                    "remote_state": f"http://remote-state:8080/terraform_state/{deploy_state}",
                    "self.project_path": f"/tmp/{self.stack_name}/{self.environment}/{self.squad}/{self.name}/{self.project_path}",
                    "stdout": result.stderr.split("\n"),
                }
            return {
                "command": "destroy",
                "deploy": self.name,
                "self.squad": self.squad,
                "self.stack_name": self.stack_name,
                "self.environment": self.environment,
                "rc": rc,
                "tfvars_files": self.variables_file,
                "self.project_path": f"/tmp/{self.stack_name}/{self.environment}/{self.squad}/{self.name}/{self.project_path}",
                "remote_state": f"http://remote-state:8080/terraform_state/{deploy_state}",
                "stdout": result.stdout.split("\n"),
            }
        except Exception:
            return {
                "command": "destroy",
                "deploy": self.name,
                "self.squad": self.squad,
                "self.stack_name": self.stack_name,
                "self.environment": self.environment,
                "rc": 1,
                "tfvars_files": self.variables_file,
                "self.project_path": f"/tmp/{self.stack_name}/{self.environment}/{self.squad}/{self.name}/{self.project_path}",
                "remote_state": f"http://remote-state:8080/terraform_state/{deploy_state}",
                "stdout": "ko",
            }


@dataclass
class SimpleActions:
    stack_name: str
    squad: str
    environment: str
    name: str

    def output_execute(self):
        try:
            get_path = f"{self.stack_name}-{self.squad}-{self.environment}-{self.name}"
            print(get_path)
            response = requests.get(
                f"{settings.REMOTE_STATE}/terraform_state/{get_path}"
            )
            json_data = response.json()
            result = json_data.get("outputs")
            if not result:
                result = jmespath.search("modules[*].outputs", json_data)
            return result
        except Exception as err:
            return {"command": "output", "rc": 1, "stdout": err}

    def unlock_execute(self):
        try:
            get_path = f"{self.stack_name}-{self.squad}-{self.environment}-{self.name}"
            response = requests.delete(
                f"{settings.REMOTE_STATE}/terraform_lock/{get_path}", json={}
            )
            return response.json()
        except Exception as err:
            return {"command": "unlock", "rc": 1, "stdout": err}

    def show_execute(self):
        try:
            get_path = f"{self.stack_name}-{self.squad}-{self.environment}-{self.name}"
            print(get_path)
            response = requests.get(
                f"{settings.REMOTE_STATE}/terraform_state/{get_path}"
            )
            json_data = response.json()
            return json_data
        except Exception as err:
            return {"command": "show", "rc": 1, "stdout": err}
