import json
from dataclasses import dataclass

import hcl
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


@dataclass
class GetVars(StructBase):
    project_path: str
    """
    In this class are the methods to obtain information from the terraform variables
    """
    def __set_path(self):
        if not self.project_path:
            return f"/tmp/{self.stack_name}/{self.environment}/{self.squad}/{self.name}/variables.tf"
        return f"/tmp/{self.stack_name}/{self.environment}/{self.squad}/{self.name}/{self.project_path}/variables.tf"

    def get_vars_json(self) -> dict:
        try:
            file_hcl = self.__set_path()
            print(file_hcl)
            with open(file_hcl, "r") as fp:
                obj = hcl.load(fp)
            if obj.get("variable"):
                return {"command": "get_vars_json", "rc": 0, "stdout": json.dumps(obj)}
            else:
                error_msg = "Variable file is empty, not iterable"
                return {"command": "get_vars_json", "rc": 1, "stdout": error_msg}
        except IOError:
            error_msg = "Variable file not accessible"
            return {"command": "get_vars_json", "rc": 1, "stdout": error_msg}
        except Exception as err:
            return {"command": "get_vars_json", "rc": 1, "stdout": err}
