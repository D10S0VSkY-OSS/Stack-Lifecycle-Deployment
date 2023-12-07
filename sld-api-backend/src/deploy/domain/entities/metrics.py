from pydantic import BaseModel
from typing import List


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
    user_activity: List[UserActivity]
    action_count: List[ActionCount]
    environment_count: List[EnvironmentCount]
    stack_usage: List[StackUsage]
    monthly_deploy_count: List[MonthlyDeployCount]
    squad_deploy_count: List[SquadDeployCount]
    cloud_provider_usage: List[CloudProviderUsage]
    squad_environment_usage: List[SquadEnvironmentUsage]
