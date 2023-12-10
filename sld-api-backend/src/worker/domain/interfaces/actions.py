from typing import Type
from abc import ABC, abstractmethod
from src.worker.domain.services.command import command
from src.worker.domain.entities.actions import StructActionsBase


class Actions(ABC):
    def __init__(self, params: StructActionsBase, command: Type[command] = command) -> None:
        self.name = params.name
        self.stack_name = params.stack_name
        self.branch = params.branch
        self.environment = params.environment
        self.squad = params.squad
        self.iac_type = params.iac_type
        self.version = params.version
        self.secreto = params.secreto
        self.variables_file = params.variables_file
        self.project_path = params.project_path
        self.task_id = params.task_id
        self.command = command

    @abstractmethod
    def execute_deployer_command(self, action: str) -> dict:
        pass
