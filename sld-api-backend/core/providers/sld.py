from abc import ABCMeta, ABC, abstractmethod


class Providers(object):
    def __init__(self, provider):
        self.provider = provider

    def execute(self, exec_command):
        return self.provider.command(exec_command)


class ProvidersInterface(ABC):
    @abstractmethod
    def command(self, command):
        raise NotImplementedError

class Terraform(ProvidersInterface):
    def command(self, command):
        return command
