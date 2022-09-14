import json
import logging
import os
import shutil
import stat
import subprocess
import zipfile
from io import BytesIO
from os import listdir, path
from os.path import isfile, join

import hcl
import jmespath
import requests
from config.api import settings
from jinja2 import Template
from security.providers_credentials import secret, unsecret


class TerraformActions:
    @staticmethod
    def binary_download(
        stack_name: str, environment: str, squad: str, version: str
    ) -> dict:
        binary = f"{settings.TERRAFORM_BIN_REPO}/{version}/terraform_{version}_linux_amd64.zip"
        try:
            if not os.path.exists(f"/tmp/{version}"):
                os.mkdir(f"/tmp/{version}")
            if not os.path.isfile(f"/tmp/{version}/terraform"):
                req = requests.get(binary)
                _zipfile = zipfile.ZipFile(BytesIO(req.content))
                _zipfile.extractall(f"/tmp/{version}")
                st = os.stat(f"/tmp/{version}/terraform")
                os.chmod(f"/tmp/{version}/terraform", st.st_mode | stat.S_IEXEC)
            return {
                "command": "binaryDownload",
                "rc": 0,
                "stdout": "Download Binary file",
            }

        except Exception as err:
            return {"command": "binaryDownload", "rc": 1, "stdout": err}

    @staticmethod
    def git_clone(
        git_repo: str,
        name: str,
        stack_name: str,
        environment: str,
        squad: str,
        branch: str,
    ) -> dict:
        try:
            directory = f"/tmp/{stack_name}/{environment}/{squad}/"
            os.makedirs(directory, exist_ok=True)
            logging.info(f"Directory {directory} created successfully")
        except OSError:
            logging.info(f"Directory {directory} can not be created")
        try:
            if os.path.exists(f"{directory}/{name}"):
                shutil.rmtree(f"{directory}/{name}")
            logging.info(f"Download git repo {git_repo} branch {branch}")
            os.chdir(f"/tmp/{stack_name}/{environment}/{squad}/")
            result = subprocess.run(
                f"git clone --recurse-submodules --branch {branch} {git_repo} {name}",
                shell=True,
                capture_output=True,
                encoding="utf8",
            )
            logging.info(f"Check if variable.tf file exist")
            tfvars_files = [
                f
                for f in listdir(directory)
                if f.endswith(".tfvars") and isfile(join(directory, f))
            ]
            rc = result.returncode
            if rc != 0:
                return {
                    "command": "git",
                    "rc": rc,
                    "tfvars": tfvars_files,
                    "stdout": result.stderr,
                }
            return {
                "command": "git",
                "rc": rc,
                "tfvars": tfvars_files,
                "stdout": result.stdout,
            }
        except Exception as err:
            return {"command": "git", "rc": 1, "tfvars": tfvars_files, "stdout": err}

    @staticmethod
    def tfstate_render(
        stack_name: str, environment: str, squad: str, project_path: str, name: str
    ) -> dict:
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
                deploy_state=f"{stack_name}-{squad}-{environment}-{name}"
            )
            file_path = f"/tmp/{stack_name}/{environment}/{squad}/{name}/{stack_name}-{name}-{environment}.tf"
            if project_path:
                file_path = f"/tmp/{stack_name}/{environment}/{squad}/{name}/{project_path}/{stack_name}-{name}-{environment}.tf"
            with open(file_path, "w") as tf_state:
                tf_state.write(provider_backend)
            return {"command": "tfserver", "rc": 0, "stdout": data}
        except Exception as err:
            return {"command": "tfserver", "rc": 1, "stderr": err}

    @staticmethod
    def data_source_render(
        stack_name: str, environment: str, squad: str, name: str
    ) -> dict:
        data = """
        data "terraform_remote_state" "generic" {
          backend = "http"
          config = {
          address = "http://remote-state:8080/terraform_state/{{deploy_state}}"
        }
        }
        """
        try:
            tm = Template(data)
            provider_backend = tm.render(
                deploy_state=f"{environment}_{stack_name}_{squad}_{name}"
            )
            with open(
                f"/tmp/{stack_name}/{environment}/{squad}/{name}/data_{environment}_{stack_name}_{name}.tf",
                "w",
            ) as tf_state:
                tf_state.write(provider_backend)
            return {"command": "datasource", "rc": 0, "stdout": data}
        except Exception as err:
            return {"command": "datasource", "rc": 1, "stdout": err}

    @staticmethod
    def tfvars(
        stack_name: str,
        environment: str,
        squad: str,
        name: str,
        project_path: str,
        **kwargs: dict,
    ) -> dict:
        try:
            file_path = f"/tmp/{stack_name}/{environment}/{squad}/{name}/{stack_name}.tfvars.json"
            if project_path:
                file_path = f"/tmp/{stack_name}/{environment}/{squad}/{name}/{project_path}/{stack_name}.tfvars.json"
            with open(file_path, "w") as tfvars_json:
                json.dump(kwargs.get("vars"), tfvars_json)
            return {"command": "tfvars", "rc": 0, "stdout": kwargs.get("vars")}
        except Exception as err:
            return {"command": "tfvars", "rc": 1, "stdout": f"{err}"}

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def delete_local_folder(dir_path: str) -> dict:
        try:
            shutil.rmtree(dir_path)
        except FileNotFoundError:
            pass
        except OSError:
            raise
