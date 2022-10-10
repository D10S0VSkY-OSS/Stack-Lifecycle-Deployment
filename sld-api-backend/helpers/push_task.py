import json

from config.api import settings
from fastapi import HTTPException
from tasks.terraform_worker import (output, pipeline_deploy, pipeline_destroy,
                                    pipeline_git_pull, pipeline_plan,
                                    schedule_add, schedule_delete,
                                    schedule_get, schedule_update,
                                    schedules_list, show, unlock)


def async_deploy(
    git_repo: str,
    name: str,
    stack_name: str,
    environment: str,
    squad: str,
    branch: str,
    tf_ver: str,
    variables: dict,
    secreto: str,
    variables_file: str = "",
    project_path: str = "",
    backend_config: str = "",
    user: str = "",
):

    queue = "any" if not settings.TASK_ROUTE else squad
    pipeline_deploy_result = pipeline_deploy.s(
        git_repo=git_repo,
        name=name,
        stack_name=stack_name,
        environment=environment,
        squad=squad,
        branch=branch,
        version=tf_ver,
        kwargs=variables,
        secreto=secreto,
        variables_file=variables_file,
        project_path=project_path,
        backend_config=backend_config,
        user=user,
    ).apply_async(
        queue=queue,
        retry=True,
        retry_policy={
            "max_retries": settings.TASK_MAX_RETRY,
            "interval_start": settings.TASK_RETRY_INTERVAL,
        },
    )

    return pipeline_deploy_result.task_id


def async_destroy(
    git_repo: str,
    name: str,
    stack_name: str,
    environment: str,
    squad: str,
    branch: str,
    tf_ver: str,
    variables: dict,
    secreto: str,
    variables_file: str = "",
    project_path: str = "",
    backend_config: str = "",
    user: str = "",
):

    queue = "any" if not settings.TASK_ROUTE else squad
    pipeline_destroy_result = pipeline_destroy.s(
        git_repo=git_repo,
        name=name,
        stack_name=stack_name,
        environment=environment,
        squad=squad,
        branch=branch,
        version=tf_ver,
        kwargs=variables,
        secreto=secreto,
        variables_file=variables_file,
        project_path=project_path,
        backend_config=backend_config,
        user=user,
    ).apply_async(
        queue=queue,
        retry=True,
        retry_policy={
            "max_retries": settings.TASK_MAX_RETRY,
            "interval_start": settings.TASK_RETRY_INTERVAL,
        },
    )

    return pipeline_destroy_result.task_id


def async_plan(
    git_repo: str,
    name: str,
    stack_name: str,
    environment: str,
    squad: str,
    branch: str,
    tf_ver: str,
    variables: dict,
    secreto: str,
    variables_file: str = "",
    project_path: str = "",
    backend_config: str = "",
    user: str = "",
):

    queue = "any" if not settings.TASK_ROUTE else squad
    pipeline_plan_result = pipeline_plan.s(
        git_repo=git_repo,
        name=name,
        stack_name=stack_name,
        environment=environment,
        squad=squad,
        branch=branch,
        version=tf_ver,
        kwargs=variables,
        secreto=secreto,
        variables_file=variables_file,
        project_path=project_path,
        backend_config=backend_config,
        user=user,
    ).apply_async(
        queue=queue,
        retry=True,
        retry_policy={
            "max_retries": settings.TASK_MAX_RETRY,
            "interval_start": settings.TASK_RETRY_INTERVAL,
        },
    )

    return pipeline_plan_result.task_id


def async_output(stack_name: str, environment: str, squad: str, name: str):
    output_result = output.s(stack_name, environment, squad, name).apply_async(
        queue="squad"
    )
    return output_result.task_id


def async_unlock(stack_name: str, squad: str, environment: str, name: str):
    unlock_result = unlock.s(stack_name, squad, environment, name).apply_async(
        queue="squad"
    )
    return unlock_result.task_id


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


def async_show(stack_name: str, environment: str, squad: str, name: str):
    show_result = show.s(stack_name, environment, squad, name).apply_async(
        queue="squad"
    )
    return show_result.task_id


def sync_git(
    stack_name: str, git_repo: str, branch: str, project_path: str, environment: str, squad: str, name: str
):
    try:
        pipeline_git_result = pipeline_git_pull.s(
            stack_name=stack_name,
            git_repo=git_repo,
            branch=branch,
            project_path=project_path,
            environment=environment,
            squad=squad,
            name=name,
        ).apply_async(queue="squad")
        task_id = pipeline_git_result.task_id
        get_data = pipeline_git_result.get()
        try:
            data = json.loads(get_data.get("stdout"))
        except Exception:
            raise ValueError(get_data.get("result"))
        return task_id, data
    except Exception as err:
        raise HTTPException(status_code=408, detail=f"{err}")


def sync_get_vars(
    stack_name: str, environment: str, squad: str, name: str, task_id, otype: str
):
    try:
        if otype == "json":
            data_json = get_variable_json.apply_async(
                queue=squad, args=(stack_name, environment, squad, name)
            )
            variables_json = json.loads(data_json.get())
            return variables_json
        elif otype == "list":
            data_list = get_variable_list.apply_async(
                queue=squad, args=(stack_name, environment, squad, name)
            )
            variables_list = data_list.get()
            return variables_list
    except Exception as err:
        raise HTTPException(
            status_code=404,
            detail=f"Variable File Not Found check task {task_id} {err}",
        )
