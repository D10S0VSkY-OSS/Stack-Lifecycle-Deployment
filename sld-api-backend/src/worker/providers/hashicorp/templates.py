import json
import logging
from dataclasses import dataclass

import hcl
from jinja2 import Template
from src.worker.helpers.hcl2_to_json import convert_to_json


@dataclass
class StructBase:
    name: str
    stack_name: str
    environment: str
    squad: str


@dataclass
class StructProject(StructBase):
    project_path: str


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
            return {"command": "tfserver", "rc": 1, "stdout": str(err)}


@dataclass
class Tfvars(StructBase):
    project_path: str
    variables: dict

    def save(self) -> dict:
        try:
            file_path = f"/tmp/{self.stack_name}/{self.environment}/{self.squad}/{self.name}/{self.name}.tfvars.json"
            if self.project_path:
                file_path = f"/tmp/{self.stack_name}/{self.environment}/{self.squad}/{self.name}/{self.project_path}/{self.name}.tfvars.json"
            with open(file_path, "w") as tfvars_json:
                json.dump(self.variables, tfvars_json)
            return {"command": "tfvars", "rc": 0, "stdout": self.variables}
        except Exception as err:
            return {"command": "tfvars", "rc": 1, "stdout": f"{err}"}


@dataclass
class GetVars(StructProject):
    """
    In this class are the methods to obtain information from the terraform variables
    """

    def __set_path(self):
        if not self.project_path:
            return f"/tmp/{self.stack_name}/{self.environment}/{self.squad}/{self.name}/variables.tf"
        return f"/tmp/{self.stack_name}/{self.environment}/{self.squad}/{self.name}/{self.project_path}/variables.tf"

    def process_dict(self, d):
        return {
            key: (
                value.replace("${", "").replace("}", "")
                if isinstance(value, str)
                else (
                    self.process_dict(value)
                    if isinstance(value, dict)
                    else [self.process_dict(item) for item in value]
                    if isinstance(value, list)
                    else value
                )
            )
            for key, value in d.items()
        }

    def get_vars_json(self) -> dict:
        try:
            file_hcl = self.__set_path()
            with open(file_hcl, "r") as fp:
                hcl_data = hcl.load(fp)
            if hcl_data.get("variable"):
                return {
                    "command": "get_vars_json",
                    "rc": 0,
                    "stdout": json.dumps(hcl_data),
                }
            else:
                error_msg = "Variable file is empty, not iterable"
                return {"command": "get_vars_json", "rc": 1, "stdout": error_msg}
        except IOError:
            error_msg = "Variable file not accessible"
            return {"command": "get_vars_json", "rc": 1, "stdout": error_msg}
        except ValueError as err:
            logging.warn(err)
            logging.warn("hclv1 cannot read variables.tf trying to read with hcl2")
            try:
                result = {"variable": convert_to_json(file_hcl)}
                return {
                    "command": "get_vars_json",
                    "rc": 0,
                    "stdout": json.dumps(result),
                }
            except Exception as err:
                error_msg = f"Syntax error in variable file(check with terraform validate): {err}"
                logging.error(error_msg)
                return {"command": "get_vars_json", "rc": 1, "stdout": error_msg}
        except Exception as err:
            return {"command": "get_vars_json", "rc": 1, "stdout": err}