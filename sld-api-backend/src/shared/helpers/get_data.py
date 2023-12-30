from functools import wraps

import redis
from celery.result import AsyncResult
from config.api import settings
from croniter import croniter
from fastapi import HTTPException

from src.activityLogs.infrastructure import repositories as crud_activity
from src.aws.infrastructure import repositories as crud_aws
from src.azure.infrastructure import repositories as crud_azure
from src.custom_providers.infrastructure import repositories as crud_custom_provider
from src.deploy.infrastructure import repositories as crud_deploys
from src.gcp.infrastructure import repositories as crud_gcp
from src.stacks.infrastructure import repositories as crud_stacks
from src.users.infrastructure import repositories as crud_users

r = redis.Redis(
    host=settings.CACHE_SERVER,
    port=6379,
    db=2,
    charset="utf-8",
    decode_responses=True,
)


def check_squad_user(squad_owner: list, squad_add: list) -> bool:
    return any(item in squad_owner for item in squad_add)


def check_role_user(role_owner: list, role_add: list) -> bool:
    less_roles = ["stormtrooper", "R2-D2", "grogu"]
    role = role_owner + less_roles
    return all(item in role for item in role_add)


def check_squad_stack(
    db, current_user: str, current_user_squad: list, stack_squad_access: list
) -> bool:
    # Check if the user with squad * not have role yoda
    if not crud_users.is_master(db, current_user):
        if "darth_vader" not in current_user.role:
            raise HTTPException(
                status_code=403, detail=f"Not enough permissions for create a stack"
            )
        if "*" in stack_squad_access and "yoda" not in current_user.role:
            raise HTTPException(
                status_code=403,
                detail="It is not possible to use * squad when role is not yoda",
            )
        if not all(__squad in current_user_squad for __squad in stack_squad_access):
            raise HTTPException(
                status_code=403,
                detail=f"Not enough permissions for some of these squads {stack_squad_access}",
            )


def user_squad_scope(db, user, squad):
    try:
        if user.isdigit():
            user_info = crud_users.get_user_by_id(db=db, id=user)
        else:
            user_info = crud_users.get_user_by_username(db=db, username=user)
        if user_info == None:
            raise ValueError(f"User {user} no exists")
        return bool(set(user_info.squad).intersection(squad))
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))


def stack(db, stack_name: str):
    try:
        stack_data = crud_stacks.get_stack_by_name(db=db, stack_name=stack_name)
        if stack_data is None:
            raise Exception("Stack Name Not Found")
        return stack_data
    except Exception as err:
        raise HTTPException(status_code=404, detail=f"{err}")


def deploy(db, deploy_id: int):
    try:
        deploy_data = crud_deploys.get_deploy_by_id(db=db, deploy_id=deploy_id)
        if deploy_data is None:
            raise Exception("Deploy id Not Found")
        return deploy_data
    except Exception as err:
        raise HTTPException(status_code=404, detail=f"{err}")


def deploy_squad(db, deploy_id: int, squad: str):
    try:
        deploy_data = crud_deploys.get_deploy_by_id_squad(
            db=db, deploy_id=deploy_id, squad=squad
        )
        if deploy_data is None:
            raise Exception("Deploy id Not Found")
        return deploy_data
    except Exception as err:
        raise HTTPException(status_code=404, detail=f"{err}")


def get_deploy(db, deploy_id: int):
    try:
        deploy_data = crud_deploys.get_deploy_by_id(db=db, deploy_id=deploy_id)
        if deploy_data is None:
            raise Exception("Deploy id Not Found")
        return deploy_data
    except Exception as err:
        raise HTTPException(status_code=404, detail=f"{err}")


def check_deploy_exist(db, deploy_name: str, squad: str, env: str, stack: str):
    data_source_check = f"{deploy_name}-{squad}-{env}-{stack}"
    try:
        db_data = crud_deploys.get_deploy_by_name_squad(
            db=db, deploy_name=deploy_name, squad=squad, environment=env
        )
        if db_data is not None:
            data_db_check = f"{db_data.name}-{db_data.squad}-{db_data.environment}-{db_data.stack_name}"
            if data_source_check == data_db_check:
                raise Exception(
                    "The name of the deployment already exists in the current squad and with specified environment"
                )
    except Exception as err:
        raise HTTPException(status_code=409, detail=f"{err}")


def check_deploy_state(task_id: str):
    result = AsyncResult(task_id)
    list_state = ["SUCCESS", "FAILURE", "REVOKED", "PENDING"]
    return any(result.state == i for i in list_state)


def check_deploy_task_pending_state(deploy_name, squad, environment, task_id=None):
    if task_id:
        result = AsyncResult(str(task_id))
        list_state = ["REVOKED"]
        if any(result.state == i for i in list_state):
            return True
    try:
        if r.exists(f"{deploy_name}-{squad}-{environment}"):
            raise Exception(
                "Task already exists in pending state waiting to be executed"
            )
    except Exception as err:
        raise HTTPException(status_code=409, detail=f"{err}")
    r.set(f"{deploy_name}-{squad}-{environment}", "Locked")
    r.expire(f"{deploy_name}-{squad}-{environment}", settings.TASK_LOCKED_EXPIRED)


def check_providers(stack_name):
    providers_support = settings.PROVIDERS_SUPPORT
    if any(i in stack_name.lower() for i in providers_support):
        return True
    else:
        raise HTTPException(
            status_code=404,
            detail=f"stack name {stack_name.lower()} no content providers support name preffix: {providers_support}",
        )


def activity_log(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        crud_activity.create_activity_log(
            db=kwargs["db"],
            username=kwargs["current_user"].username,
            squad=kwargs["current_user"].squad,
            action=f'Delete User {kwargs["user"]}',
        )
        return await func(*args, **kwargs)

    return wrapper


def check_cron_schedule(cron_time: str):
    if cron_time:
        if not croniter.is_valid(cron_time):
            raise ValueError("Cron time its no valid")
    return True


async def check_prefix(db, stack_name: str, environment: str, squad: str):
    try:
        if any(i in stack_name.lower() for i in settings.AWS_PREFIX):
            secreto = await crud_aws.get_credentials_aws_profile(
                db=db, environment=environment, squad=squad
            )
            return secreto
        elif any(i in stack_name.lower() for i in settings.GCLOUD_PREFIX):
            secreto = await crud_gcp.get_credentials_gcloud_profile(
                db=db, environment=environment, squad=squad
            )
            return secreto
        elif any(i in stack_name.lower() for i in settings.AZURE_PREFIX):
            secreto = await crud_azure.get_credentials_azure_profile(
                db=db, environment=environment, squad=squad
            )
            return secreto
        elif any(i in stack_name.lower() for i in settings.CUSTOM_PREFIX):
            secreto = crud_custom_provider.get_credentials_custom_provider_profile(
                db=db, environment=environment, squad=squad
            )
            return secreto
        else:
            raise HTTPException(
                status_code=404,
                detail=f"stack name {stack_name.lower()} no content providers support name preffix: {settings.PROVIDERS_SUPPORT} ",
            )
    except Exception as err:
        raise HTTPException(
            status_code=400,
            detail=f"stack name {stack_name.lower()} env {environment} error {err}  ",
        )
