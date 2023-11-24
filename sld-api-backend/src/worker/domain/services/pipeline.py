
from src.worker.domain.entities.worker import DeployParams, DownloadGitRepoParams, DownloadBinaryParams, RemoteStateParams, TfvarsParams, PlanParams, ApplyParams
from src.worker.domain.services.provider import ProviderActions, ProviderGetVars, ProviderRequirements

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
        return self.provider.binary_download(
            self.params.version, 
        )

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

class plan:
    def __init__(self, params: PlanParams, provider: ProviderActions):
        self.params = params
        self.provider = provider

    def __call__(self):
        return self.provider.plan(
            self.params.name,
            self.params.stack_name,
            self.params.branch,
            self.params.environment,
            self.params.squad,
            self.params.version,
            self.params.secreto,
            self.params.variables_file,
            self.params.project_path,
        )

class apply:
    def __init__(self, params: ApplyParams, provider: ProviderActions):
        self.params = params
        self.provider = provider

    def __call__(self):
        return self.provider.apply(
            self.params.name,
            self.params.stack_name,
            self.params.branch,
            self.params.environment,
            self.params.squad,
            self.params.version,
            self.params.secreto,
            self.params.variables_file,
            self.params.project_path,
        )
    