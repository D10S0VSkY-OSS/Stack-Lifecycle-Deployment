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

    def execute_terraform_command(self, command: str) -> dict:
        try:
            secret(self.stack_name, self.environment, self.squad, self.name, self.secreto)
            deploy_state = f"{self.environment}_{self.stack_name}_{self.squad}_{self.name}"

            variables_files = (
                f"{self.stack_name}.tfvars.json"
                if not self.variables_file
                else self.variables_file
            )

            if not self.project_path:
                os.chdir(f"/tmp/{self.stack_name}/{self.environment}/{self.squad}/{self.name}")
            else:
                os.chdir(f"/tmp/{self.stack_name}/{self.environment}/{self.squad}/{self.name}/{self.project_path}")

            init_command = f"/tmp/{self.version}/terraform init -input=false --upgrade"
            plan_command = f"/tmp/{self.version}/terraform {command} -input=false -refresh -no-color -var-file={variables_files} -out={self.stack_name}.tfplan"
            apply_command = f"/tmp/{self.version}/terraform {command} -input=false -auto-approve -no-color {self.stack_name}.tfplan"
            destroy_command = f"/tmp/{self.version}/terraform {command} -input=false -auto-approve -no-color -var-file={variables_files}"

            result = subprocess.run(init_command, shell=True, capture_output=True, encoding="utf8")
            result = subprocess.run(plan_command, shell=True, capture_output=True, encoding="utf8")

            if command == "apply":
                result = subprocess.run(apply_command, shell=True, capture_output=True, encoding="utf8")
            elif command == "destroy":
                result = subprocess.run(destroy_command, shell=True, capture_output=True, encoding="utf8")

            unsecret(self.stack_name, self.environment, self.squad, self.name, self.secreto)

            rc = result.returncode

            output_data = {
                "command": command,
                "deploy": self.name,
                "squad": self.squad,
                "stack_name": self.stack_name,
                "environment": self.environment,
                "rc": rc,
                "tfvars_files": self.variables_file,
                "remote_state": f"http://remote-state:8080/terraform_state/{deploy_state}",
                "project_path": f"/tmp/{self.stack_name}/{self.environment}/{self.squad}/{self.name}/{self.project_path}",
                "stdout": result.stderr.split("\n") if rc != 0 else result.stdout.split("\n"),
            }

            return output_data

        except Exception as e:
            return {
                "command": command,
                "deploy": self.name,
                "squad": self.squad,
                "stack_name": self.stack_name,
                "environment": self.environment,
                "rc": 1,
                "tfvars_files": self.variables_file,
                "project_path": f"/tmp/{self.stack_name}/{self.environment}/{self.squad}/{self.name}/{self.project_path}",
                "remote_state": f"http://remote-state:8080/terraform_state/{deploy_state}",
                "stdout": "ko",
                "error_message": str(e),
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
