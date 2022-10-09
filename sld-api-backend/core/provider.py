# DI terraform provider
from core.providers.hashicorp.actions import Actions, SimpleActions
from core.providers.hashicorp.artifact import Artifact
from core.providers.hashicorp.download import BinaryDownload
from core.providers.hashicorp.templates import Backend, GetVars, Tfvars


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
        artifact=Artifact,
    ) -> dict:
        config_artifact = artifact(
            name, stack_name, environment, squad, git_repo, branch
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
        kwargs: dict,
        vars=Tfvars,
    ) -> dict:
        config_vars = vars(name, stack_name, environment, squad, project_path, kwargs)
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
        vars=GetVars,
    ) -> dict:
        config_vars = vars(name, stack_name, environment, squad)
        return config_vars.get_vars_json()


class ProviderActions:
    """
    This class contains the typical methods of a deployment
    """
    def plan(
        name: str,
        stack_name: str,
        branch: str,
        environment: str,
        squad: str,
        version: str,
        secreto: dict,
        variables_file: str = "",
        project_path: str = "",
        action=Actions,
    ) -> dict:
        config_action = action(
            name,
            stack_name,
            branch,
            environment,
            squad,
            version,
            secreto,
            variables_file,
            project_path,
        )
        return config_action.plan_execute()

    def apply(
        name: str,
        stack_name: str,
        branch: str,
        environment: str,
        squad: str,
        version: str,
        secreto: dict,
        variables_file: str = "",
        project_path: str = "",
        action=Actions,
    ) -> dict:
        config_action = action(
            name,
            stack_name,
            branch,
            environment,
            squad,
            version,
            secreto,
            variables_file,
            project_path,
        )
        return config_action.apply_execute()

    def destroy(
        name: str,
        stack_name: str,
        branch: str,
        environment: str,
        squad: str,
        version: str,
        secreto: dict,
        variables_file: str = "",
        project_path: str = "",
        action=Actions,
    ) -> dict:
        config_action = action(
            name,
            stack_name,
            branch,
            environment,
            squad,
            version,
            secreto,
            variables_file,
            project_path,
        )
        return config_action.destroy_execute()

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
