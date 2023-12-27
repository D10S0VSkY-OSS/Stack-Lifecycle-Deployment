import datetime
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, desc, case

import src.deploy.domain.entities.deploy as schemas_deploy
from src.deploy.domain.entities.repository import DeployFilter, DeployFilterResponse
from src.deploy.domain.entities.metrics import ActionCount, EnvironmentCount, MonthlyDeployCount, SquadDeployCount, StackUsage, UserActivity, CloudProviderUsage, SquadEnvironmentUsage
import src.deploy.infrastructure.models as models
from src.stacks.infrastructure.models import Stack


def create_new_deploy(
    db: Session,
    deploy: schemas_deploy.DeployCreate,
    stack_branch: str,
    action: str,
    user_id: int,
    squad: str,
    task_id: str,
    username: str,
):
    db_deploy = models.Deploy(
        name=deploy.name,
        stack_name=deploy.stack_name,
        stack_branch=stack_branch,
        environment=deploy.environment,
        tfvar_file=deploy.tfvar_file,
        project_path=deploy.project_path,
        variables=deploy.variables,
        action=action,
        username=username,
        user_id=user_id,
        task_id=task_id,
        start_time=deploy.start_time,
        destroy_time=deploy.destroy_time,
        created_at=datetime.datetime.now(),
        squad=squad,
    )
    try:
        db.add(db_deploy)
        db.commit()
        db.refresh(db_deploy)
        return db_deploy
    except Exception as err:
        raise err


def update_deploy(
    db: Session,
    deploy_id: int,
    action: str,
    username: str,
    user_id: int,
    task_id: str,
    start_time: str,
    destroy_time: str,
    stack_branch: str,
    tfvar_file: str,
    project_path: str,
    variables: dict,
):
    db_deploy = db.query(models.Deploy).filter(models.Deploy.id == deploy_id).first()

    db_deploy.action = action
    db_deploy.task_id = task_id
    db_deploy.username = username
    db_deploy.user_id = user_id
    db_deploy.stack_branch = stack_branch
    db_deploy.tfvar_file = tfvar_file
    db_deploy.project_path = project_path
    db_deploy.variables = variables
    db_deploy.updated_at = datetime.datetime.now()
    check_None = ["string"]
    if db_deploy.start_time not in check_None:
        db_deploy.start_time = start_time
    if db_deploy.destroy_time not in check_None:
        db_deploy.destroy_time = destroy_time
    try:
        db.add(db_deploy)
        db.commit()
        db.refresh(db_deploy)
        return db_deploy
    except Exception as err:
        raise err


def update_plan(db: Session, deploy_id: int, action: str, task_id: str):

    db_deploy = db.query(models.Deploy).filter(models.Deploy.id == deploy_id).first()

    db_deploy.action = action
    db_deploy.task_id = task_id
    try:
        db.add(db_deploy)
        db.commit()
        db.refresh(db_deploy)
        return db_deploy
    except Exception as err:
        raise err


def update_schedule(db: Session, deploy_id: int, start_time: str, destroy_time: str):

    db_deploy = db.query(models.Deploy).filter(models.Deploy.id == deploy_id).first()

    db_deploy.start_time = start_time
    db_deploy.destroy_time = destroy_time
    try:
        db.add(db_deploy)
        db.commit()
        db.refresh(db_deploy)
        return db_deploy
    except Exception as err:
        raise err


def delete_deploy_by_id(db: Session, deploy_id: int, squad: str):
    db.query(models.Deploy).filter(models.Deploy.id == deploy_id).filter(
        models.Deploy.squad == squad
    ).delete()
    try:
        db.commit()
        return {models.Deploy.id: "deleted", "Deploy_id": deploy_id}
    except Exception as err:
        raise err


def get_deploy_by_id(db: Session, deploy_id: int):
    try:
        return db.query(models.Deploy).filter(models.Deploy.id == deploy_id).first()
    except Exception as err:
        raise err


def get_deploy_by_name(db: Session, deploy_name: str):
    try:
        return db.query(models.Deploy).filter(models.Deploy.name == deploy_name).first()
    except Exception as err:
        raise err


def get_deploy_by_stack(db: Session, stack_name: str):
    try:
        return (
            db.query(models.Deploy)
            .filter(models.Deploy.stack_name == stack_name)
            .first()
        )
    except Exception as err:
        raise err


def get_deploy_by_id_squad(db: Session, deploy_id: int, squad: str):
    try:
        return (
            db.query(models.Deploy)
            .filter(models.Deploy.id == deploy_id)
            .filter(models.Deploy.squad == squad)
            .first()
        )
    except Exception as err:
        raise err


def get_deploy_by_name_squad(
    db: Session, deploy_name: str, squad: str, environment: str
):
    try:
        return (
            db.query(models.Deploy)
            .filter(models.Deploy.name == deploy_name)
            .filter(models.Deploy.squad == squad)
            .filter(models.Deploy.environment == environment)
            .first()
        )
    except Exception as err:
        raise err


def get_all_deploys(db: Session, skip: int = 0, limit: int = 100):
    try:
        return db.query(models.Deploy).order_by(desc(models.Deploy.id)).offset(skip).limit(limit).all()
    except Exception as err:
        raise err


def get_all_deploys_by_squad(db: Session, squad: str, skip: int = 0, limit: int = 100):
    try:
        result = []
        for i in squad:
            result.extend(
                db.query(models.Deploy).filter(models.Deploy.squad == i).all()
            )
        return set(result)
    except Exception as err:
        raise err


def get_deploys(db: Session, filters: DeployFilter, skip: int = 0, limit: int = 100) -> List[DeployFilterResponse]:
    query = db.query(models.Deploy, Stack.icon_path).join(
        Stack, models.Deploy.stack_name == Stack.stack_name
    )
    for field, value in filters.model_dump().items():
        if value is not None:
            if field == 'squad' and isinstance(value, list):
                query = query.filter(getattr(models.Deploy, field).in_(value))
            else:
                query = query.filter(getattr(models.Deploy, field) == value)

    results = query.order_by(desc(models.Deploy.id)).offset(skip).limit(limit).all()

    deploy_responses = []
    for deploy, icon_path in results:
        deploy_dict = deploy.__dict__
        deploy_dict['icon_path'] = icon_path
        deploy_responses.append(DeployFilterResponse(**deploy_dict))

    return deploy_responses


class MetricsFetcher:
    def __init__(self, db: Session):
        self.db = db

    def get_deploy_count_by_user(self) -> List[UserActivity]:
        query_result = self.db.query(
            models.Deploy.username, 
            func.count(models.Deploy.id)
        ).group_by(models.Deploy.username).all()
        return [UserActivity(username=username, deploy_count=count) for username, count in query_result]

    def get_deploy_count_by_action(self) -> List[ActionCount]:
        query_result = self.db.query(
            models.Deploy.action, 
            func.count(models.Deploy.id)
        ).group_by(models.Deploy.action).all()
        return [ActionCount(action=action, count=count) for action, count in query_result]

    def get_deploy_count_by_environment(self) -> List[EnvironmentCount]:
        query_result = self.db.query(
            models.Deploy.environment, 
            func.count(models.Deploy.id)
        ).group_by(models.Deploy.environment).all()
        return [EnvironmentCount(environment=environment, count=count) for environment, count in query_result]

    def get_deploy_count_by_stack_name(self) -> List[StackUsage]:
        query_result = self.db.query(
            models.Deploy.stack_name, 
            func.count(models.Deploy.id)
        ).group_by(models.Deploy.stack_name).all()
        return [StackUsage(stack_name=stack_name, count=count) for stack_name, count in query_result]

    def get_monthly_deploy_count(self) -> List[MonthlyDeployCount]:
        query_result = self.db.query(
            extract('month', models.Deploy.created_at), 
            func.count(models.Deploy.id)
        ).group_by(extract('month', models.Deploy.created_at)).all()
        return [MonthlyDeployCount(month=month, count=count) for month, count in query_result]

    def get_deploy_count_by_squad(self) -> List[SquadDeployCount]:
        query_result = self.db.query(
            models.Deploy.squad, 
            func.count(models.Deploy.id)
        ).group_by(models.Deploy.squad).all()
        return [SquadDeployCount(squad=squad, count=count) for squad, count in query_result]

    def get_cloud_provider_usage(self) -> List[CloudProviderUsage]:
        stacks = self.db.query(models.Deploy.stack_name).all()
        counts = {'aws': 0, 'azure': 0, 'gcp': 0, 'custom': 0}

        for (stack_name,) in stacks:
            for provider in counts.keys():
                if stack_name.startswith(provider + '_'):
                    counts[provider] += 1
                    break

        return [CloudProviderUsage(provider=provider, count=count) 
                for provider, count in counts.items() if count > 0]

    def get_squad_environment_usage(self) -> List[SquadEnvironmentUsage]:
        results = self.db.query(
            models.Deploy.squad,
            models.Deploy.environment,
            func.count(models.Deploy.id)
        ).group_by(
            models.Deploy.squad,
            models.Deploy.environment
        ).all()

        return [
            SquadEnvironmentUsage(squad=squad, environment=environment, count=count)
            for squad, environment, count in results
        ]