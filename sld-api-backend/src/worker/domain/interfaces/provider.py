from abc import ABC


class IProviderArtifactRequirements(ABC):
    @staticmethod
    def artifact_download(name, stack_name, environment, squad, git_repo, branch, project_path):
        pass
