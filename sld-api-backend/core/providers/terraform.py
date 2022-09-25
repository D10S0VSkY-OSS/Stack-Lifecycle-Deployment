from distutils.command.config import config
from inspect import stack
import json
import logging
import os
from re import A
import shutil
import stat
import subprocess
import zipfile
from io import BytesIO
from os import listdir, path
from os.path import isfile, join

import hcl
import jmespath
from config.api import settings
from jinja2 import Template
from security.providers_credentials import secret, unsecret


#DI terraform provider
from core.providers.hashicorp.download import BinaryDownload
from core.providers.hashicorp.artifact import Artifact
from core.providers.hashicorp.templates import Backend, Tfvars

class TerraformRequirements:
    '''
    In this class, everything that is needed so that terraformActions can be executed is generated.
    '''
    def binaryFunction(version, binary_download = BinaryDownload):
        binaryMethod = binary_download(version)
        return binaryMethod.get()


    def artifactoryFunction(
        name: str,
        stack_name: str,
        environment: str,
        squad: str,
        git_repo: str,
        branch: str,
        artifact = Artifact
    ) -> dict:
        getArtifact = artifact(
            name,
            stack_name,
            environment,
            squad,
            git_repo,
            branch
        )
        return getArtifact.get()

    def storageState(
        name: str,
        stack_name: str,
        environment: str,
        squad: str,
        project_path: str, 
        backend = Backend
        ) -> dict:
        configBackend = backend(name,stack_name,environment,squad,project_path)
        return configBackend.save()


    def parameterVars(
        name: str,
        stack_name: str,
        environment: str,
        squad: str,
        project_path: str,
        kwargs: dict,
        vars = Tfvars,
        ) -> dict:
        configVars = vars(name,stack_name,environment,squad,project_path,kwargs)
        return configVars.save()


class TerraformGetVars:
    '''
    In this class are the methods to obtain information from the terraform variables
    '''

    def get_vars_tfvars(stack_name: str, environment: str, squad: str, name: str):
        if path.exists(
            f"/tmp/{ stack_name }/{environment}/{squad}/{name}/{stack_name}.tfvars.json"
        ):
            with open(
                f"/tmp/{ stack_name }/{environment}/{squad}/{name}/{stack_name}.tfvars.json",
                "r",
            ) as tfvars:
                tf = tfvars.read()
            return json.loads(tf)
        else:
            return {
                "action": f"terraform.tfvars not exist in module {stack_name}",
                "rc": 1,
            }

    def get_vars_list(stack_name: str, environment: str, squad: str, name: str) -> list:
        try:
            file_hcl = f"/tmp/{ stack_name }/{environment}/{squad}/{name}/variables.tf"
            with open(file_hcl, "r") as fp:
                obj = hcl.load(fp)
            if obj.get("variable"):
                lista = [i for i in obj.get("variable")]
                return {"command": "get_vars_list", "rc": 0, "stdout": lista}
            else:
                error_msg = "Variable file is empty, not iterable"
                return {"command": "get_vars_list", "rc": 1, "stdout": error_msg}
        except IOError:
            error_msg = "Variable file not accessible"
            return {"command": "get_vars_list", "rc": 1, "stdout": error_msg}
        except Exception as err:
            return {"command": "get_vars_list", "rc": 1, "stdout": err}

    def get_vars_json(stack_name: str, environment: str, squad: str, name: str) -> dict:
        try:
            file_hcl = f"/tmp/{stack_name}/{environment}/{squad}/{name}/variables.tf"
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


class TerraformUtils:
    '''
    Class where methods similar to a helper are added
    '''
    def delete_local_folder(dir_path: str) -> dict:
        try:
            shutil.rmtree(dir_path)
        except FileNotFoundError:
            pass
        except OSError:
            raise


class TerraformActions:
    '''
    In this class are all the methods equivalent to the terraform commands
    '''

    def plan_execute(
        stack_name: str,
        environment: str,
        squad: str,
        name: str,
        version: str,
        variables_file: str = "",
        project_path: str = "",
        **secreto: dict,
    ) -> dict:
        try:
            secret(stack_name, environment, squad, name, secreto)
            deploy_state = f"{environment}_{stack_name}_{squad}_{name}"
            # Execute task
            variables_files = (
                f"{stack_name}.tfvars.json"
                if variables_file == "" or variables_file == None
                else variables_file
            )

            if not project_path:
                os.chdir(f"/tmp/{stack_name}/{environment}/{squad}/{name}")
            os.chdir(f"/tmp/{stack_name}/{environment}/{squad}/{name}/{project_path}")

            result = subprocess.run(
                f"/tmp/{version}/terraform init -input=false --upgrade",
                shell=True,
                capture_output=True,
                encoding="utf8",
            )
            result = subprocess.run(
                f"/tmp/{version}/terraform plan -input=false -refresh -no-color -var-file={variables_files} -out={stack_name}.tfplan",
                shell=True,
                capture_output=True,
                encoding="utf8",
            )
            unsecret(stack_name, environment, squad, name, secreto)

            # Capture events
            rc = result.returncode
            # check result
            if rc != 0:
                return {
                    "command": "plan",
                    "deploy": name,
                    "squad": squad,
                    "stack_name": stack_name,
                    "environment": environment,
                    "rc": rc,
                    "tfvars_files": variables_file,
                    "remote_state": f"http://remote-state:8080/terraform_state/{deploy_state}",
                    "project_path": f"/tmp/{stack_name}/{environment}/{squad}/{name}/{project_path}",
                    "stdout": [result.stderr.split("\n")],
                }
            return {
                "command": "plan",
                "deploy": name,
                "squad": squad,
                "stack_name": stack_name,
                "environment": environment,
                "rc": rc,
                "tfvars_files": variables_file,
                "project_path": f"/tmp/{stack_name}/{environment}/{squad}/{name}/{project_path}",
                "remote_state": f"http://remote-state:8080/terraform_state/{deploy_state}",
                "stdout": [result.stdout.split("\n")],
            }
        except Exception:
            return {
                "command": "plan",
                "deploy": name,
                "squad": squad,
                "stack_name": stack_name,
                "environment": environment,
                "rc": 1,
                "tfvars_files": variables_file,
                "project_path": f"/tmp/{stack_name}/{environment}/{squad}/{name}/{project_path}",
                "remote_state": f"http://remote-state:8080/terraform_state/{deploy_state}",
                "stdout": [result.stderr.split("\n")],
            }

    def apply_execute(
        stack_name: str,
        branch: str,
        environment: str,
        squad: str,
        name: str,
        version: str,
        variables_file: str = "",
        project_path: str = "",
        **secreto: dict,
    ) -> dict:
        try:
            secret(stack_name, environment, squad, name, secreto)
            deploy_state = f"{environment}_{stack_name}_{squad}_{name}"
            # Execute task
            variables_files = (
                f"{stack_name}.tfvars.json"
                if variables_file == "" or variables_file == None
                else variables_file
            )

            if not project_path:
                os.chdir(f"/tmp/{stack_name}/{environment}/{squad}/{name}")
            os.chdir(f"/tmp/{stack_name}/{environment}/{squad}/{name}/{project_path}")

            result = subprocess.run(
                f"/tmp/{version}/terraform init -input=false --upgrade",
                shell=True,
                capture_output=True,
                encoding="utf8",
            )
            result = subprocess.run(
                f"/tmp/{version}/terraform apply -input=false -auto-approve -no-color {stack_name}.tfplan",
                shell=True,
                capture_output=True,
                encoding="utf8",
            )
            unsecret(stack_name, environment, squad, name, secreto)

            # Capture events
            rc = result.returncode
            # check result
            if rc != 0:
                return {
                    "command": "apply",
                    "deploy": name,
                    "squad": squad,
                    "stack_name": stack_name,
                    "environment": environment,
                    "rc": rc,
                    "tfvars_files": variables_file,
                    "remote_state": f"http://remote-state:8080/terraform_state/{deploy_state}",
                    "project_path": f"/tmp/{stack_name}/{environment}/{squad}/{name}/{project_path}",
                    "stdout": [result.stderr.split("\n")],
                }
            return {
                "command": "apply",
                "deploy": name,
                "squad": squad,
                "stack_name": stack_name,
                "environment": environment,
                "rc": rc,
                "tfvars_files": variables_file,
                "project_path": f"/tmp/{stack_name}/{environment}/{squad}/{name}/{project_path}",
                "remote_state": f"http://remote-state:8080/terraform_state/{deploy_state}",
                "stdout": [result.stdout.split("\n")],
            }
        except Exception:
            return {
                "command": "apply",
                "deploy": name,
                "squad": squad,
                "stack_name": stack_name,
                "environment": environment,
                "rc": 1,
                "tfvars_files": variables_file,
                "project_path": f"/tmp/{stack_name}/{environment}/{squad}/{name}/{project_path}",
                "remote_state": f"http://remote-state:8080/terraform_state/{deploy_state}",
                "stdout": "ko",
            }

    def destroy_execute(
        stack_name: str,
        branch: str,
        environment: str,
        squad: str,
        name: str,
        version: str,
        variables_file: str = "",
        project_path: str = "",
        **secreto: dict,
    ) -> dict:
        try:
            secret(stack_name, environment, squad, name, secreto)
            deploy_state = f"{environment}_{stack_name}_{squad}_{name}"
            # Execute task
            variables_files = (
                f"{stack_name}.tfvars.json"
                if variables_file == "" or variables_file == None
                else variables_file
            )
            if not project_path:
                os.chdir(f"/tmp/{stack_name}/{environment}/{squad}/{name}")
            os.chdir(f"/tmp/{stack_name}/{environment}/{squad}/{name}/{project_path}")

            result = subprocess.run(
                f"/tmp/{version}/terraform init -input=false --upgrade",
                shell=True,
                capture_output=True,
                encoding="utf8",
            )
            result = subprocess.run(
                f"/tmp/{version}/terraform destroy -input=false -auto-approve -no-color -var-file={variables_files}",
                shell=True,
                capture_output=True,
                encoding="utf8",
            )
            unsecret(stack_name, environment, squad, name, secreto)
            # Capture events
            rc = result.returncode
            # check result
            if rc != 0:
                return {
                    "command": "destroy",
                    "deploy": name,
                    "squad": squad,
                    "stack_name": stack_name,
                    "environment": environment,
                    "rc": rc,
                    "tfvars_files": variables_file,
                    "remote_state": f"http://remote-state:8080/terraform_state/{deploy_state}",
                    "project_path": f"/tmp/{stack_name}/{environment}/{squad}/{name}/{project_path}",
                    "stdout": [result.stderr.split("\n")],
                }
            return {
                "command": "destroy",
                "deploy": name,
                "squad": squad,
                "stack_name": stack_name,
                "environment": environment,
                "rc": rc,
                "tfvars_files": variables_file,
                "project_path": f"/tmp/{stack_name}/{environment}/{squad}/{name}/{project_path}",
                "remote_state": f"http://remote-state:8080/terraform_state/{deploy_state}",
                "stdout": [result.stdout.split("\n")],
            }
        except Exception:
            return {
                "command": "destroy",
                "deploy": name,
                "squad": squad,
                "stack_name": stack_name,
                "environment": environment,
                "rc": 1,
                "tfvars_files": variables_file,
                "project_path": f"/tmp/{stack_name}/{environment}/{squad}/{name}/{project_path}",
                "remote_state": f"http://remote-state:8080/terraform_state/{deploy_state}",
                # "stdout": [result.stderr.split("\n")],
                "stdout": "ko",
            }

    def output_execute(stack_name: str, environment: str, squad: str, name: str):
        try:
            import requests

            get_path = f"{stack_name}-{squad}-{environment}-{name}"
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

    def unlock_execute(stack_name: str, environment: str, squad: str, name: str):
        try:
            import requests

            get_path = f"{stack_name}-{squad}-{environment}-{name}"
            response = requests.delete(
                f"{settings.REMOTE_STATE}/terraform_lock/{get_path}", json={}
            )
            json_data = response.json()
            result = json_data
            return result
        except Exception as err:
            return {"command": "unlock", "rc": 1, "stdout": err}

    def show_execute(stack_name: str, environment: str, squad: str, name: str):
        try:
            import requests

            get_path = f"{stack_name}-{squad}-{environment}-{name}"
            response = requests.get(
                f"{settings.REMOTE_STATE}/terraform_state/{get_path}"
            )
            json_data = response.json()
            return json_data
        except Exception as err:
            return {"command": "show", "rc": 1, "stdout": err}



