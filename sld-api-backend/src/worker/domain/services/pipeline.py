
from src.worker.domain.entities.worker import DeployParams, DownloadGitRepoParams, DownloadBinaryParams, RemoteStateParams, TfvarsParams, PlanParams, ApplyParams, DestroyParams, GetVariablesParams
from src.worker.domain.services.provider import ProviderActions, ProviderGetVars, ProviderRequirements
import redis
from config.api import settings
import logging


r = redis.Redis(
    host=settings.CACHE_SERVER,
    port=6379,
    db=2,
    charset="utf-8",
    decode_responses=True,
)


class DownloadGitRepo:
    def __init__(self, params: DownloadGitRepoParams, provider: ProviderRequirements):
        self.params = params
        self.provider = provider

    def __call__(self):
        return self.provider.artifact_download(
            self.params.name, 
            self.params.stack_name, 
            self.params.environment, 
            self.params.squad, 
            self.params.git_repo, 
            self.params.branch,
            self.params.project_path
        )


class DownloadBinary:
    def __init__(self, params: DownloadBinaryParams, provider: ProviderRequirements):
        self.params = params
        self.provider = provider

    def __call__(self):
        return self.provider.binary_download(self.params)


class RemoteState:
    def __init__(self, params: RemoteStateParams, provider: ProviderRequirements):
        self.params = params
        self.provider = provider

    def __call__(self):
        return self.provider.storage_state(
            self.params.name, 
            self.params.stack_name, 
            self.params.environment, 
            self.params.squad, 
            self.params.project_path
        )


class Tfvars:
    def __init__(self, params: TfvarsParams, provider: ProviderRequirements):
        self.params = params
        self.provider = provider

    def __call__(self):
        return self.provider.parameter_vars(
            self.params.name, 
            self.params.stack_name, 
            self.params.environment, 
            self.params.squad, 
            self.params.project_path, 
            self.params.variables
        )


class GetVariables:
    def __init__(self, params: GetVariablesParams, provider: ProviderGetVars):
        self.params = params
        self.provider = provider

    def __call__(self):
        return self.provider.json_vars(
            self.params.name,
            self.params.stack_name,
            self.params.environment,
            self.params.squad, 
            self.params.project_path
        )


class plan:
    def __init__(self, params: PlanParams, provider: ProviderActions):
        self.params = params
        self.provider = provider

    def __call__(self):
        return self.provider.plan(self.params)


class apply:
    def __init__(self, params: ApplyParams, provider: ProviderActions):
        self.params = params
        self.provider = provider

    def __call__(self):
        return self.provider.apply(self.params)


class destroy:
    def __init__(self, params: DeployParams, provider: ProviderActions):
        self.params = params
        self.provider = provider

    def __call__(self):
        return self.provider.destroy(self.params)


# PIPELINE
class Pipeline:
    def __init__(self, params: DeployParams):
        self.params = params

    def locked_task(self):
        logging.info(f"Checking if task {self.params.name}-{self.params.squad}-{self.params.environment} is locked in cache server {settings.CACHE_SERVER}")
        logging.info(f"Locking task {self.params.name}-{self.params.squad}-{self.params.environment}")
        r.set(f"{self.params.name}-{self.params.squad}-{self.params.environment}", "Locked")
        r.expire(f"{self.params.name}-{self.params.squad}-{self.params.environment}", settings.TASK_LOCKED_EXPIRED)

    def unlock_task(self):
        r.delete(f"{self.params.name}-{self.params.squad}-{self.params.environment}")

    # Git clone repo
    def download_git_repo(self):
        git_params = DownloadGitRepoParams(
            git_repo=self.params.git_repo,
            name=self.params.name,
            stack_name=self.params.stack_name,
            environment=self.params.environment,
            squad=self.params.squad,
            branch=self.params.branch,
            project_path=self.params.project_path
        )
        download_git_repo = DownloadGitRepo(params=git_params, provider=ProviderRequirements)
        download_git_repo_result = download_git_repo()
        if download_git_repo_result["rc"] != 0:
            raise Exception(download_git_repo_result)
        return download_git_repo_result
    
    # Download terrafom
    def download_binary(self):
        binary_params = DownloadBinaryParams(
            iac_type=self.params.iac_type,
            version=self.params.version
        )
        download_binary = DownloadBinary(params=binary_params, provider=ProviderRequirements)
        download_binary_result = download_binary()
        if download_binary_result["rc"] != 0:
            raise Exception(download_binary_result)
        return download_binary_result

    # Create tf to use the custom backend state
    def set_remote_state(self):
        remote_state_params = RemoteStateParams(
            name=self.params.name,
            stack_name=self.params.stack_name,
            environment=self.params.environment,
            squad=self.params.squad,
            project_path=self.params.project_path
        )
        remote_state = RemoteState(params=remote_state_params, provider=ProviderRequirements)
        remote_state_result = remote_state()
        if remote_state_result["rc"] != 0:
            raise Exception(remote_state_result)
        return remote_state_result

    # Create tfvar serialize with json
    def set_tfvars(self):
        tfvars_params = TfvarsParams(
            name=self.params.name,
            stack_name=self.params.stack_name,
            environment=self.params.environment,
            squad=self.params.squad,
            project_path=self.params.project_path,
            variables=self.params.variables
        )
        tfvars = Tfvars(params=tfvars_params, provider=ProviderRequirements)
        tfvars_result = tfvars()
        if tfvars_result["rc"] != 0:
            raise Exception(tfvars_result)
        return tfvars_result
    
    def get_variables(self):
        get_variables_params = GetVariablesParams(
            name=self.params.name,
            stack_name=self.params.stack_name,
            environment=self.params.environment,
            squad=self.params.squad,
            project_path=self.params.project_path
        )
        get_variables = GetVariables(params=get_variables_params, provider=ProviderGetVars)
        get_variables_result = get_variables()
        if get_variables_result["rc"] != 0:
            raise Exception(get_variables_result)
        return get_variables_result

    # Plan execute
    def execute_plan(self):
        plan_params = DeployParams(
            git_repo=self.params.git_repo,
            name=self.params.name,
            stack_name=self.params.stack_name,
            environment=self.params.environment,
            squad=self.params.squad,
            branch=self.params.branch,
            iac_type=self.params.iac_type,
            version=self.params.version,
            variables=self.params.variables,
            project_path=self.params.project_path,
            secreto=self.params.secreto,
            variables_file=self.params.variables_file,
            user=self.params.user,
            task_id=self.params.task_id
        )
        plan_execute = plan(params=plan_params, provider=ProviderActions)
        plan_result = plan_execute()
        if plan_result["rc"] != 0:
            raise Exception(plan_result)
        return plan_result

    # Apply execute
    def execute_apply(self):
        apply_params = DeployParams(
            git_repo=self.params.git_repo,
            name=self.params.name,
            stack_name=self.params.stack_name,
            environment=self.params.environment,
            squad=self.params.squad,
            branch=self.params.branch,
            iac_type=self.params.iac_type,
            version=self.params.version,
            variables=self.params.variables,
            project_path=self.params.project_path,
            secreto=self.params.secreto,
            variables_file=self.params.variables_file,
            user=self.params.user,
            task_id=self.params.task_id
        )
        apply_execute = apply(params=apply_params, provider=ProviderActions)
        apply_result = apply_execute()
        if apply_result["rc"] != 0:
            raise Exception(apply_result)
        return apply_result

    # Destroy execute 
    def execute_destroy(self):
        destroy_params = DeployParams(
            git_repo=self.params.git_repo,
            name=self.params.name,
            stack_name=self.params.stack_name,
            environment=self.params.environment,
            squad=self.params.squad,
            branch=self.params.branch,
            version=self.params.version,
            iac_type=self.params.iac_type,
            variables=self.params.variables,
            project_path=self.params.project_path,
            secreto=self.params.secreto,
            variables_file=self.params.variables_file,
            user=self.params.user,
            task_id=self.params.task_id
        )
        destroy_execute = destroy(params=destroy_params, provider=ProviderActions)
        destroy_result = destroy_execute()
        if destroy_result["rc"] != 0:
            raise Exception(destroy_result)
        return destroy_result
