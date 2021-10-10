from fastapi import HTTPException
from celery.result import AsyncResult
from datetime import datetime
from functools import wraps
from croniter import croniter
import redis

from crud import stacks as crud_stacks
from crud import deploys as crud_deploys
from crud import user as crud_users
from crud import activityLogs as crud_activity
from config.api import settings

r = redis.Redis(host=settings.BACKEND_SERVER, port=6379, db=2,
                charset="utf-8", decode_responses=True)

def user_squad_scope(db, user, squad):
    try:
        if user.isdigit():
            user_info = crud_users.get_user_by_id(db=db, id=user)
        else:
            user_info = crud_users.get_user_by_username(db=db, username=user)
        if user_info == None:
            raise ValueError(f"User {user} no exists")
        if user_info.squad == squad:
            return True
    except Exception as err:
        raise HTTPException(
            status_code=400,
            detail=str(err))


def stack(db, stack_name: str):
    try:
        stack_data = crud_stacks.get_stack_by_name(
            db=db, stack_name=stack_name)
        if stack_data is None:
            raise Exception("Stack Name Not Found")
        return stack_data
    except Exception as err:
        raise HTTPException(
            status_code=404,
            detail=f"{err}")


def deploy(db, deploy_id: int):
    try:
        deploy_data = crud_deploys.get_deploy_by_id(
            db=db, deploy_id=deploy_id)
        if deploy_data is None:
            raise Exception("Deploy id Not Found")
        return deploy_data
    except Exception as err:
        raise HTTPException(
            status_code=404,
            detail=f"{err}")


def deploy_squad(db, deploy_id: int, squad: str):
    try:
        deploy_data = crud_deploys.get_deploy_by_id_squad(
            db=db, deploy_id=deploy_id, squad=squad)
        if deploy_data is None:
            raise Exception("Deploy id Not Found")
        return deploy_data
    except Exception as err:
        raise HTTPException(
            status_code=404,
            detail=f"{err}")


def get_deploy(db, deploy_id: int):
    try:
        deploy_data = crud_deploys.get_deploy_by_id(
            db=db, deploy_id=deploy_id)
        if deploy_data is None:
            raise Exception("Deploy id Not Found")
        return deploy_data
    except Exception as err:
        raise HTTPException(
            status_code=404,
            detail=f"{err}")


def check_deploy_exist(db, deploy_name: str, squad: str, env: str, stack: str):
    data_source_check = f'{deploy_name}-{squad}-{env}-{stack}'
    try:
        db_data = crud_deploys.get_deploy_by_name_squad(
            db=db, deploy_name=deploy_name, squad=squad, environment=env)
        if db_data is not None:
            data_db_check = f'{db_data.name}-{db_data.squad}-{db_data.environment}-{db_data.stack_name}'
            print("Soy get_Data linea 92 y no estoy NONE")
            if data_source_check == data_db_check:
                raise Exception(
                    "The name of the deployment already exists in the current squad and with specified environment")
    except Exception as err:
        raise HTTPException(
            status_code=409,
            detail=f"{err}")


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
            raise Exception("Task already exists in pending state waiting to be executed")
    except Exception as err:
        raise HTTPException(
            status_code=409, detail=f"{err}")
    r.set(f"{deploy_name}-{squad}-{environment}", "Locked")
    r.expire(f"{deploy_name}-{squad}-{environment}", settings.TASK_LOCKED_EXPIRED)


def check_providers(stack_name):
    providers_support = settings.PROVIDERS_SUPPORT
    if any(i in stack_name.lower() for i in providers_support):
        return True
    else:
        raise HTTPException(
            status_code=404,
            detail=f"stack name {stack_name.lower()} no content providers support name preffix: {providers_support}")


def activity_log(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        crud_activity.create_activity_log(
            db=kwargs['db'],
            username=kwargs['current_user'].username,
            squad=kwargs['current_user'].squad,
            action=f'Delete User {kwargs["user"]}'
        )
        return await func(*args, **kwargs)

    return wrapper


def check_cron_schedule(cron_time: str):
    if cron_time:
        if not croniter.is_valid(cron_time):
            raise ValueError("Cron time its no valid")
    return True
