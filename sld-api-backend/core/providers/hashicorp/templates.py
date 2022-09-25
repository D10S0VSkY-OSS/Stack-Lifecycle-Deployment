from dataclasses import dataclass
import json
from jinja2 import Template

@dataclass
class StructBase:
    name: str
    stack_name: str
    environment: str
    squad: str
    

@dataclass
class Backend(StructBase):
    project_path: str

    def save(self) -> dict:
        data = """
        terraform {
          backend "http" {
            address = "http://remote-state:8080/terraform_state/{{deploy_state}}"
            lock_address = "http://remote-state:8080/terraform_lock/{{deploy_state}}"
            lock_method = "PUT"
            unlock_address = "http://remote-state:8080/terraform_lock/{{deploy_state}}"
            unlock_method = "DELETE"
          }
        }
        """
        try:
            tm = Template(data)
            provider_backend = tm.render(
                deploy_state=f"{self.stack_name}-{self.squad}-{self.environment}-{self.name}"
            )
            file_path = f"/tmp/{self.stack_name}/{self.environment}/{self.squad}/{self.name}/{self.stack_name}-{self.name}-{self.environment}.tf"
            if self.project_path:
                file_path = f"/tmp/{self.stack_name}/{self.environment}/{self.squad}/{self.name}/{self.project_path}/{self.stack_name}-{self.name}-{self.environment}.tf"
            with open(file_path, "w") as tf_state:
                tf_state.write(provider_backend)
            return {"command": "tfserver", "rc": 0, "stdout": data}
        except Exception as err:
            return {"command": "tfserver", "rc": 1, "stderr": err}


@dataclass
class Tfvars(StructBase):
    project_path: str
    kwargs: dict
    def save(self) -> dict:
        try:
            file_path = f"/tmp/{self.stack_name}/{self.environment}/{self.squad}/{self.name}/{self.stack_name}.tfvars.json"
            if self.project_path:
                file_path = f"/tmp/{self.stack_name}/{self.environment}/{self.squad}/{self.name}/{self.project_path}/{self.stack_name}.tfvars.json"
            with open(file_path, "w") as tfvars_json:
                json.dump(self.kwargs, tfvars_json)
            return {"command": "tfvars", "rc": 0, "stdout": self.kwargs}
        except Exception as err:
            return {"command": "tfvars", "rc": 1, "stdout": f"{err}"}