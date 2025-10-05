from pydantic import BaseModel


class UserActivity(BaseModel):
    username: str
    deploy_count: int


class ActionCount(BaseModel):
    action: str
    count: int


class EnvironmentCount(BaseModel):
    environment: str
    count: int


class StackUsage(BaseModel):
    stack_name: str
    count: int


class MonthlyDeployCount(BaseModel):
    month: int
    count: int


class SquadDeployCount(BaseModel):
    squad: str
    count: int


class CloudProviderUsage(BaseModel):
    provider: str
    count: int


class SquadEnvironmentUsage(BaseModel):
    squad: str
    environment: str
    count: int


class AllMetricsResponse(BaseModel):
    user_activity: list[UserActivity]
    action_count: list[ActionCount]
    environment_count: list[EnvironmentCount]
    stack_usage: list[StackUsage]
    monthly_deploy_count: list[MonthlyDeployCount]
    squad_deploy_count: list[SquadDeployCount]
    cloud_provider_usage: list[CloudProviderUsage]
    squad_environment_usage: list[SquadEnvironmentUsage]
