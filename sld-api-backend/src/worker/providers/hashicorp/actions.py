import os
from dataclasses import dataclass
import jmespath
import requests
from config.api import settings

from src.worker.security.providers_credentials import secret, unsecret
from src.worker.domain.services.command import command

@dataclass
class StructBase:
    name: str
    stack_name: str
    branch: str
    environment: str
    squad: str


@dataclass
class Actions(StructBase):
    iac_type: str
    version: str
    secreto: dict
    variables_file: str
    project_path: str
    task_id: str
    subprocess_handler: command = command

    def execute_terraform_command(self, action: str) -> dict:
        channel = self.task_id
        try:
            secret(self.stack_name, self.environment, self.squad, self.name, self.secreto)
            deploy_state = f"{self.environment}_{self.stack_name}_{self.squad}_{self.name}"

            variables_files = (
                f"{self.name}.tfvars.json"
                if not self.variables_file
                else self.variables_file
            )

            if not self.project_path:
                os.chdir(f"/tmp/{self.stack_name}/{self.environment}/{self.squad}/{self.name}")
            else:
                os.chdir(f"/tmp/{self.stack_name}/{self.environment}/{self.squad}/{self.name}/{self.project_path}")

            init_command = f"/tmp/{self.version}/{self.iac_type} init -no-color -input=false --upgrade"
            plan_command = f"/tmp/{self.version}/{self.iac_type} plan -input=false -refresh -no-color -var-file={variables_files} -out={self.name}.tfplan"
            apply_command = f"/tmp/{self.version}/{self.iac_type} apply -input=false -auto-approve -no-color {self.name}.tfplan"
            destroy_command = f"/tmp/{self.version}/{self.iac_type} destroy -input=false -auto-approve -no-color -var-file={variables_files}"
            output = []
            if action == "plan":
                result, output_init = command(init_command, channel=channel)
                result, output_plan = self.subprocess_handler(plan_command, channel=channel)
                output = output_init + output_plan
            if action == "apply":
                result, output_apply = self.subprocess_handler(apply_command, channel=channel)
                output = output + output_apply
            elif action == "destroy":
                result, output_init = command(init_command, channel=channel)
                result, output_destroy = self.subprocess_handler(destroy_command, channel=channel)
                output = output_init + output_destroy

            unsecret(self.stack_name, self.environment, self.squad, self.name, self.secreto)

            rc = result

            output_data = {
                "command": action,
                "deploy": self.name,
                "squad": self.squad,
                "stack_name": self.stack_name,
                "environment": self.environment,
                "rc": rc,
                "tfvars_files": self.variables_file,
                "remote_state": f"http://remote-state:8080/terraform_state/{deploy_state}",
                "project_path": f"/tmp/{self.stack_name}/{self.environment}/{self.squad}/{self.name}/{self.project_path}",
                "stdout": output,
            }

            return output_data

        except Exception:
            return {
                "command": action,
                "deploy": self.name,
                "squad": self.squad,
                "stack_name": self.stack_name,
                "environment": self.environment,
                "rc": 1,
                "tfvars_files": self.variables_file,
                "project_path": f"/tmp/{self.stack_name}/{self.environment}/{self.squad}/{self.name}/{self.project_path}",
                "remote_state": f"http://remote-state:8080/terraform_state/{deploy_state}",
                "stdout": output,
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
            response = requests.get(
                f"{settings.REMOTE_STATE}/terraform_state/{get_path}"
            )
            json_data = response.json()
            return json_data
        except Exception as err:
            return {"command": "show", "rc": 1, "stdout": err}
