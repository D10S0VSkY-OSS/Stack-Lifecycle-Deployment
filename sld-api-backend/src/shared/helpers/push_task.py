import json

from config.api import settings
from fastapi import HTTPException

from src.worker.domain.entities.worker import DeployParams, DownloadGitRepoParams
from src.worker.tasks.terraform_worker import (
    pipeline_deploy,
    pipeline_destroy,
    pipeline_git_pull,
    pipeline_plan,
    schedule_add,
    schedule_delete,
    schedule_get,
    schedule_update,
    schedules_list,
)


def async_deploy(deploy_params: DeployParams):
    queue = "any" if not settings.TASK_ROUTE else deploy_params.squad
    pipeline_deploy_result = pipeline_deploy.s(deploy_params.model_dump()).apply_async(
        queue=queue,
        retry=True,
        retry_policy={
            "max_retries": settings.TASK_MAX_RETRY,
            "interval_start": settings.TASK_RETRY_INTERVAL,
        },
    )
    return pipeline_deploy_result.task_id


def async_destroy(destroy_params: DeployParams):
    queue = "any" if not settings.TASK_ROUTE else destroy_params.squad
    pipeline_destroy_result = pipeline_destroy.s(destroy_params.model_dump()).apply_async(
        queue=queue,
        retry=True,
        retry_policy={
            "max_retries": settings.TASK_MAX_RETRY,
            "interval_start": settings.TASK_RETRY_INTERVAL,
        },
    )
    return pipeline_destroy_result.task_id


def async_plan(plan_params: DeployParams):
    queue = "any" if not settings.TASK_ROUTE else plan_params.squad
    pipeline_deploy_result = pipeline_plan.s(plan_params.model_dump()).apply_async(
        queue=queue,
        retry=True,
        retry_policy={
            "max_retries": settings.TASK_MAX_RETRY,
            "interval_start": settings.TASK_RETRY_INTERVAL,
        },
    )
    return pipeline_deploy_result.task_id


def async_schedule_delete(deploy_name: str, squad: str):
    deploy_schedule_delete_result = schedule_delete.s(deploy_name).apply_async(
        queue="squad"
    )
    return deploy_schedule_delete_result.task_id


def async_schedule_add(deploy_name: str, squad: str):
    deploy_schedule_add_result = schedule_add.s(deploy_name).apply_async(queue="squad")
    return deploy_schedule_add_result.task_id


def async_schedule_list(squad: str):
    schedule_list_result = schedules_list.s().apply_async(queue="squad")
    return schedule_list_result.task_id


def async_schedule_get(deploy_name, squad: str):
    schedule_get_result = schedule_get.s(deploy_name).apply_async(queue="squad")
    return schedule_get_result.task_id


def async_schedule_update(deploy_name: str):
    schedule_update_result = schedule_update.s(deploy_name).apply_async(queue="squad")
    return schedule_update_result.task_id


def sync_git(
    stack_name: str,
    git_repo: str,
    branch: str,
    project_path: str,
    environment: str,
    squad: str,
    name: str,
):
    git_params = DownloadGitRepoParams(
        git_repo=git_repo,
        name=name,
        stack_name=stack_name,
        environment=environment,
        squad=squad,
        branch=branch,
        project_path=project_path,
    )
    try:
        pipeline_git_result = pipeline_git_pull.s(git_params.model_dump()).apply_async(queue="squad")
        task_id = pipeline_git_result.task_id
        get_data = pipeline_git_result.get()
        try:
            data = json.loads(get_data.get("stdout"))
        except Exception:
            raise ValueError(get_data.get("result"))
        return task_id, data
    except Exception as err:
        raise HTTPException(status_code=408, detail=f"{err}")