# DI terraform provider
from src.worker.providers.hashicorp.actions import Actions, SimpleActions
from src.worker.providers.hashicorp.artifact import Artifact
from src.worker.providers.hashicorp.download import BinaryDownload
from src.worker.providers.hashicorp.templates import Backend, GetVars, Tfvars
from src.worker.domain.entities.worker import DeployParams


class ProviderRequirements:
    """
    In this class, everything that is needed so that ProviderActions can be executed is generated.
    """

    def binary_download(version, binary=BinaryDownload):
        config_binary = binary(version)
        return config_binary.get()

    def artifact_download(
        name: str,
        stack_name: str,
        environment: str,
        squad: str,
        git_repo: str,
        branch: str,
        project_path: str = "",
        artifact=Artifact,
    ) -> dict:
        config_artifact = artifact(
            name, stack_name, environment, squad, git_repo, branch, project_path
        )
        return config_artifact.get()

    def storage_state(
        name: str,
        stack_name: str,
        environment: str,
        squad: str,
        project_path: str,
        backend=Backend,
    ) -> dict:
        config_backend = backend(name, stack_name, environment, squad, project_path)
        return config_backend.save()

    def parameter_vars(
        name: str,
        stack_name: str,
        environment: str,
        squad: str,
        project_path: str,
        variables: dict,
        vars=Tfvars,
    ) -> dict:
        config_vars = vars(name, stack_name, environment, squad, project_path, variables)
        return config_vars.save()


class ProviderGetVars:
    """
    In this class are the methods to obtain information from the provider variables
    """

    def json_vars(
        name: str,
        stack_name: str,
        environment: str,
        squad: str,
        project_path: str,
        vars=GetVars,
    ) -> dict:
        config_vars = vars(name, stack_name, environment, squad, project_path)
        return config_vars.get_vars_json()


class ProviderActions:
    """
    This class contains the typical methods of a deployment
    """

    def plan(params: DeployParams, action: Actions = Actions) -> dict:
        config_action = action(
            params.name,
            params.stack_name,
            params.branch,
            params.environment,
            params.squad,
            params.version,
            params.secreto,
            params.variables_file,
            params.project_path,
        )
        return config_action.execute_terraform_command("plan")

    def apply(params: DeployParams, action: Actions = Actions) -> dict:
        config_action = action(
            params.name,
            params.stack_name,
            params.branch,
            params.environment,
            params.squad,
            params.version,
            params.secreto,
            params.variables_file,
            params.project_path,
        )
        return config_action.execute_terraform_command("apply")

    def destroy(params: DeployParams, action: Actions = Actions) -> dict:
        config_action = action(
            params.name,
            params.stack_name,
            params.branch,
            params.environment,
            params.squad,
            params.version,
            params.secreto,
            params.variables_file,
            params.project_path,
        )
        return config_action.execute_terraform_command("destroy")

    def output(
        stack_name: str, squad: str, environment: str, name: str, action=SimpleActions
    ) -> dict:
        config_action = action(stack_name, squad, environment, name)
        return config_action.output_execute()

    def unlock(
        stack_name: str, squad: str, environment: str, name: str, action=SimpleActions
    ) -> dict:
        config_action = action(stack_name, squad, environment, name)
        return config_action.unlock_execute()

    def show(
        stack_name: str, squad: str, environment: str, name: str, action=SimpleActions
    ) -> dict:
        config_action = action(stack_name, squad, environment, name)
        return config_action.show_execute()
