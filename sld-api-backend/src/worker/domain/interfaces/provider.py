from abc import ABC, abstractmethod
class IProviderArtifactRequirements(ABC):
    @staticmethod
    def artifact_download(name, stack_name, environment, squad, git_repo, branch, project_path):
        # logic to download artifact
        pass