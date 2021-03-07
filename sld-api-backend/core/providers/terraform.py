import os
import json
import logging
import subprocess
import jmespath
from os import path

import hcl
import shutil
import ansible_runner
from jinja2 import Template
from config.api import settings
from security.providers_credentials import secret, unsecret

os.environ['ANSIBLE_NOCOLOR'] = "True"


class TerraformActions(object):

    @staticmethod
    def binaryDownload(
            stack_name: str,
            environment: str,
            squad: str,
            version: str
    ) -> dict:
        binary = f'{settings.TERRAFORM_BIN_REPO}/{version}/terraform_{version}_linux_amd64.zip'
        try:
            runner_response = ansible_runner.run(
                rotate_artifacts=1,
                private_data_dir=f'/tmp/{stack_name}/{environment}/{squad}',
                host_pattern='localhost',
                module='file',
                module_args=f'path=/tmp/{version} state=directory',
            )
            runner_response = ansible_runner.run(
                rotate_artifacts=1,
                private_data_dir=f'/tmp/{stack_name}/{environment}/{squad}',
                host_pattern='localhost',
                module='unarchive',
                module_args=f'src={binary} dest=/tmp/{version} remote_src=True',
            )
            logs = [i for i in runner_response.events]
            binaryDownload_stdout = jmespath.search(
                '[*].event_data.res.stdout_lines', logs)
            binaryDownload_stderr = jmespath.search(
                '[*].event_data.res.msg', logs)
            rc = runner_response.rc
            # check result
            if rc != 0:
                return {"command": "binaryDownload", "rc": rc, "stdout": binaryDownload_stderr}
            return {"command": "binaryDownload", "rc": rc, "stdout": binaryDownload_stdout}
        except Exception as err:
            return {"command": "binaryDownload", "rc": 1, "stdout": str(err)}

    @staticmethod
    def gitClone(
            git_repo: str,
            name: str,
            stack_name: str,
            environment: str,
            squad: str,
            branch: str
    ) -> dict:
        try:
            logging.info(f"Download git repo {git_repo} branch {branch}")
            runner_response = ansible_runner.run(
                private_data_dir='/tmp/',
                host_pattern='localhost',
                verbosity=0,
                module='git',
                module_args=f'repo={git_repo} dest={stack_name}/{environment}/{squad}/{name} version={branch} force=yes',
            )
            logs = [i for i in runner_response.events]
            git_stdout = jmespath.search(
                '[*].event_data.res.stdout_lines', logs)
            git_stderr = jmespath.search('[*].event_data.res.msg', logs)
            rc = runner_response.rc
            if rc != 0:
                return {"command": "git", "rc": rc, "stdout": git_stderr}
            return {"command": "git", "rc": rc, "stdout": git_stdout}
        except Exception as err:
            return {"command": "git", "rc": 1, "stdout": err}

    @staticmethod
    def tftstateRender(
            stack_name: str,
            environment: str,
            squad: str,
            name: str) -> dict:
        data = '''
        terraform {
          backend "http" {
            address = "http://remote-state:8080/terraform_state/{{deploy_state}}"
            lock_address = "http://remote-state:8080/terraform_lock/{{deploy_state}}"
            lock_method = "PUT"
            unlock_address = "http://remote-state:8080/terraform_lock/{{deploy_state}}"
            unlock_method = "DELETE"
          }
        }
        '''
        try:
            tm = Template(data)
            provider_backend = tm.render(
                deploy_state=f'{stack_name}-{squad}-{environment}-{name}')
            with open(f'/tmp/{stack_name}/{environment}/{squad}/{name}/{stack_name}-{name}-{environment}.tf', 'w') as tf_state:
                tf_state.write(provider_backend)
            return {"command": "tfserver", "rc": 0, "stdout": data}
        except Exception as err:
            return {"command": "tfserver", "rc": 1, "stderr": err}

    @staticmethod
    def dataSourceRender(
            stack_name: str,
            environment: str,
            squad: str,
            name: str) -> dict:
        data = '''
        data "terraform_remote_state" "generic" {
          backend = "http"
          config = {
          address = "http://remote-state:8080/terraform_state/{{deploy_state}}"
        }
        }
        '''
        try:
            tm = Template(data)
            provider_backend = tm.render(
                deploy_state=f'{environment}_{stack_name}_{squad}_{name}')
            with open(f'/tmp/{stack_name}/{environment}/{squad}/{name}/data_{environment}_{stack_name}_{name}.tf', 'w') as tf_state:
                tf_state.write(provider_backend)
            return {"command": "dataSorce", "rc": 0, "stdout": data}
        except Exception as err:
            return {"command": "datasource", "rc": 1, "stdout": err}

    @staticmethod
    def tfvars(
            stack_name: str,
            environment: str,
            squad: str,
            name: str,
            **kwargs: dict) -> dict:
        try:
            with open(f'/tmp/{stack_name}/{environment}/{squad}/{name}/{stack_name}.tfvars.json', 'w') as tfvars_json:
                json.dump(kwargs.get("vars"), tfvars_json)
            return {"command": "dataSorce", "rc": 0, "stdout": kwargs.get("vars")}
        except Exception as err:
            return {"command": "datasource", "rc": 1, "stdout": f'{err}'}

    @staticmethod
    def planExcute(
            stack_name: str,
            environment: str,
            squad: str,
            name: str,
            version: str,
            **secreto: dict) -> dict:
        try:
            secret(stack_name, environment, squad, name, secreto)
            # Execute task
            runner_response = ansible_runner.run(
                private_data_dir=f'/tmp/{stack_name}/{environment}/{squad}/{name}',
                host_pattern='localhost',
                module='terraform',
                module_args=f'binary_path=/tmp/{version}/terraform '
                            f'force_init=True project_path=/tmp/{stack_name}/{environment}/{squad}/{name} '
                            f'plan_file=/tmp/{stack_name}/{environment}/{squad}/{name}/{stack_name}.tfplan '
                            f'variables_files={stack_name}.tfvars.json state=planned',
            )
            unsecret(stack_name, environment, squad, name, secreto)

            # Capture events
            logs = [i for i in runner_response.events]
            plan_stdout = jmespath.search(
                '[*].event_data.res.stdout_lines', logs)
            plan_stderr = jmespath.search('[*].event_data.res.msg', logs)
            rc = runner_response.rc
            # check result
            if rc != 0:
                return {"command": "apply", "rc": rc, "stdout": plan_stderr}
            return {"command": "apply", "rc": rc, "stdout": plan_stdout}
        except Exception as err:
            return {"command": "plan", "rc": 1, "stdout": f'{err}'}

    @staticmethod
    def applyExecute(
            stack_name: str,
            environment: str,
            squad: str,
            name: str,
            version: str,
            **secreto: dict) -> dict:
        try:
            secret(stack_name, environment, squad, name, secreto)
            # Execute task
            runner_response = ansible_runner.run(
                private_data_dir=f'/tmp/{stack_name}/{environment}/{squad}/{name}',
                host_pattern='localhost',
                module='terraform',
                module_args=f'binary_path=/tmp/{version}/terraform lock=True force_init=True project_path=/tmp/{stack_name}/{environment}/{squad}/{name} '
                            f'plan_file=/tmp/{stack_name}/{environment}/{squad}/{name}/{stack_name}.tfplan state=present',
            )
            unsecret(stack_name, environment, squad, name, secreto)
            # Capture events
            apply_logs = [i for i in runner_response.events]
            apply_stdout = jmespath.search(
                '[*].event_data.res.stdout_lines', apply_logs)
            apply_stderr = jmespath.search(
                '[*].event_data.res.msg', apply_logs)
            rc = runner_response.rc
            # check result
            if rc != 0:
                return {"command": "apply", "rc": rc, "stdout": apply_stderr}
            return {"command": "apply", "rc": rc, "stdout": apply_stdout}
        except Exception as err:
            return {"command": "apply", "rc": 1, "stdout": f'{err}'}

    @staticmethod
    def destroyExecute(
            stack_name: str,
            environment: str,
            squad: str,
            name: str,
            version: str,
            **secreto: dict) -> dict:
        try:
            secret(stack_name, environment, squad, name, secreto)
            # Execute task
            runner_response = ansible_runner.run(
                private_data_dir=f'/tmp/{stack_name}/{environment}/{squad}/{name}',
                host_pattern='localhost',
                module='terraform',
                module_args=f'binary_path=/tmp/{version}/terraform force_init=True project_path=/tmp/{stack_name}/{environment}/{squad}/{name} '
                            f'variables_files={stack_name}.tfvars.json state=absent',
            )
            unsecret(stack_name, environment, squad, name, secreto)
            # Capture events
            destroy_logs = [i for i in runner_response.events]
            destroy_stdout = jmespath.search(
                '[*].event_data.res.stdout_lines', destroy_logs)
            destroy_stderr = jmespath.search(
                '[*].event_data.res.msg', destroy_logs)
            rc = runner_response.rc
            if rc != 0:
                return {"command": "apply", "rc": rc, "stdout": destroy_stderr}
            return {"command": "apply", "rc": rc, "stdout": destroy_stdout}
        except Exception as err:
            return {"command": "apply", "rc": 1, "stdout": f'{err}'}

    @staticmethod
    def outputExecute(
            stack_name: str,
            environment: str,
            squad: str,
            name: str):
        try:
            import requests
            get_path = f'{stack_name}-{squad}-{environment}-{name}'
            response = requests.get(f'{settings.REMOTE_STATE}/terraform_state/{get_path}')
            json_data = response.json()
            result = json_data.get('outputs')
            return result
        except Exception as err:
            return {"command": "output", "rc": 1, "stdout": err}

    @staticmethod
    def UnlockExecute(
            stack_name: str,
            environment: str,
            squad: str,
            name: str):
        try:
            import requests
            get_path = f'{stack_name}-{squad}-{environment}-{name}'
            response = requests.delete(f'{settings.REMOTE_STATE}/terraform_lock/{get_path}', json={})
            json_data = response.json()
            result = json_data
            return result
        except Exception as err:
            return {"command": "unlock", "rc": 1, "stdout": err}

    @staticmethod
    def showExecute(
            stack_name: str,
            environment: str,
            squad: str,
            name: str):
        try:
            import requests
            get_path = f'{stack_name}-{squad}-{environment}-{name}'
            response = requests.get(f'{settings.REMOTE_STATE}/terraform_state/{get_path}')
            json_data = response.json()
            return json_data
        except Exception as err:
            return {"command": "output", "rc": 1, "stdout": err}

    @staticmethod
    def getVarsTfvars(
            stack_name: str,
            environment: str,
            squad: str,
            name: str):
        if path.exists(
                f"/tmp/{ stack_name }/{environment}/{squad}/{name}/{stack_name}.tfvars.json"):
            with open(f"/tmp/{ stack_name }/{environment}/{squad}/{name}/{stack_name}.tfvars.json", "r") as tfvars:
                tf = tfvars.read()
            return json.loads(tf)
        else:
            return {
                "action": f"terraform.tfvars not exist in module {stack_name}",
                "rc": 1}

    @staticmethod
    def getVarsList(
            stack_name: str,
            environment: str,
            squad: str,
            name: str) -> list:
        try:
            file_hcl = f"/tmp/{ stack_name }/{environment}/{squad}/{name}/variables.tf"
            with open(file_hcl, 'r') as fp:
                obj = hcl.load(fp)
            if obj.get('variable'):
                lista = [i for i in obj.get('variable')]
                return lista
            else:
                raise Exception('Variable file is empty, not iterable')
        except IOError:
            return {"result": "Variable file not accessible"}
        except Exception:
            return {"result": "Variable file is empty, not iterable"}

    @staticmethod
    def getVarsJson(
            stack_name: str,
            environment: str,
            squad: str,
            name: str) -> dict:
        try:
            file_hcl = f"/tmp/{stack_name}/{environment}/{squad}/{name}/variables.tf"
            with open(file_hcl, 'r') as fp:
                obj = hcl.load(fp)
            if obj.get('variable'):
                return json.dumps(obj)
            else:
                raise Exception('Variable file is empty, not iterable')
        except IOError:
            return {"result": "Variable file not accessible"}
        except Exception:
            return {"result": "Variable file is empty, not iterable"}

    @staticmethod
    def deleteLocalFolder(dir_path: str) -> dict:
        try:
            shutil.rmtree(dir_path)
        except FileNotFoundError:
            pass
        except OSError:
            raise
