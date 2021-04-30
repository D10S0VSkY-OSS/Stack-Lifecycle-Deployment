import json
from fastapi import HTTPException
from tasks.celery_worker import (
    git, unlock, schedule_add, schedule_delete,
    output, get_variable_json, get_variable_list, show, pipelineDeploy,
    pipelineDestroy, pipelinePlan, schedules_list, schedule_get
)
from config.api import settings


def asyncDeploy(
        git_repo: str,
        name: str,
        stack_name: str,
        environment: str,
        squad: str,
        branch: str,
        tf_ver: str,
        variables: dict,
        secreto: str):

    pipeline_deploy = pipelineDeploy.s(
        git_repo=git_repo,
        name=name,
        stack_name=stack_name,
        environment=environment,
        squad=squad,
        branch=branch,
        version=tf_ver,
        kwargs=variables,
        secreto=secreto
    ).apply_async(queue=squad,
                  retry=True,
                  retry_policy={
                      'max_retries': settings.TASK_MAX_RETRY,
                      'interval_start': settings.TASK_RETRY_INTERVAL,
                  }
                  )

    return pipeline_deploy.task_id


def asyncDestroy(
        git_repo: str,
        name: str,
        stack_name: str,
        environment: str,
        squad: str,
        branch: str,
        tf_ver: str,
        variables: dict,
        secreto: str):

    pipeline_destroy = pipelineDestroy.s(
        git_repo=git_repo,
        name=name,
        stack_name=stack_name,
        environment=environment,
        squad=squad,
        branch=branch,
        version=tf_ver,
        kwargs=variables,
        secreto=secreto
    ).apply_async(
        queue=squad,
        retry=True,
        retry_policy={
            'max_retries': settings.TASK_MAX_RETRY,
            'interval_start': settings.TASK_RETRY_INTERVAL,
        }
    )

    return pipeline_destroy.task_id


def asyncPlan(
        git_repo: str,
        name: str,
        stack_name: str,
        environment: str,
        squad: str,
        branch: str,
        tf_ver: str,
        variables: dict,
        secreto: str):
    pipeline_plan = pipelinePlan.s(
        git_repo=git_repo,
        name=name,
        stack_name=stack_name,
        environment=environment,
        squad=squad,
        branch=branch,
        version=tf_ver,
        kwargs=variables,
        secreto=secreto
    ).apply_async(queue=squad,
                  retry=True,
                  retry_policy={
                      'max_retries': settings.TASK_MAX_RETRY,
                      'interval_start': settings.TASK_RETRY_INTERVAL,
                  }
                  )

    return pipeline_plan.task_id


def asyncOutput(stack_name: str, environment: str, squad: str, name: str):
    pipeline_output = output.s(stack_name, environment, squad,
                               name).apply_async(queue="squad")
    return pipeline_output.task_id


def asyncUnlock(stack_name: str, environment: str, squad: str, name: str):
    pipeline_unlock = unlock.s(stack_name, environment, squad,
                               name).apply_async(queue="squad")
    return pipeline_unlock.task_id


def asyncScheduleDelete(deploy_name: str, squad: str):
    deploy_schedule_delete = schedule_delete.s(deploy_name).apply_async(queue="squad")
    return deploy_schedule_delete.task_id

def asyncScheduleAdd(deploy_name: str, squad: str):
    deploy_schedule_add = schedule_add.s(deploy_name).apply_async(queue="squad")
    return deploy_schedule_add.task_id

def asyncScheduleList(squad: str):
    pipeline_schedule_list = schedules_list.s().apply_async(queue="squad")
    return pipeline_schedule_list.task_id

def asyncScheduleGet(deploy_name, squad: str):
    pipeline_schedule_get = schedule_get.s(deploy_name).apply_async(queue="squad")
    return pipeline_schedule_get.task_id

def asyncShow(stack_name: str, environment: str, squad: str, name: str):
    pipeline_show = show.s(stack_name, environment, squad,
                               name).apply_async(queue="squad")
    return pipeline_show.task_id


def syncGit(
        stack_name: str,
        git_repo: str,
        branch: str,
        environment: str,
        squad: str,
        name: str):
    try:
        pipeline_git = git.s(
            stack_name=stack_name,
            git_repo=git_repo,
            branch=branch,
            environment=environment,
            squad=squad,
            name=name).delay()
        pipeline_git.get()
        task_id = pipeline_git.task_id
        return task_id
    except Exception as err:
        raise HTTPException(status_code=408,
                            detail=f"git TimeoutError {err}")


def syncGetVars(
        stack_name: str,
        environment: str,
        squad: str,
        name: str,
        task_id,
        otype: str):
    try:
        if otype == "json":
            data_json = get_variable_json.apply_async(
                queue=squad, args=(stack_name, environment, squad, name))
            variables_json = json.loads(data_json.get())
            return variables_json
        elif otype == "list":
            data_list = get_variable_list.apply_async(
                queue=squad, args=(stack_name, environment, squad, name))
            variables_list = data_list.get()
            return variables_list
    except Exception as err:
        raise HTTPException(
            status_code=404,
            detail=f"Variable File Not Found check task {task_id} {err}")
