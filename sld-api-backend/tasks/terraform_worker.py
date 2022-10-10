import logging
import traceback

import redis
from celery import states
from celery.exceptions import Ignore
from celery.utils.log import get_task_logger
from config.api import settings
from config.celery_config import celery_app
from core.provider import (ProviderActions, ProviderGetVars,
                           ProviderRequirements)
from helpers.folders import Utils
from helpers.metrics import push_metric
from helpers.schedule import request_url

r = redis.Redis(
    host=settings.BACKEND_SERVER,
    port=6379,
    db=2,
    charset="utf-8",
    decode_responses=True,
)

logger = get_task_logger(__name__)


@celery_app.task(
    bind=True, acks_late=True, time_limit=settings.DEPLOY_TMOUT, name="pipeline Deploy"
)
@push_metric()
def pipeline_deploy(
    self,
    git_repo: str,
    name: str,
    stack_name: str,
    environment: str,
    squad: str,
    branch: str,
    version: str,
    kwargs: any,
    secreto: str,
    variables_file: str = "",
    project_path: str = "",
    backend_config: str = "",
    user: str = "",
):
    filter_kwargs = {key: value for (key, value) in kwargs.items() if "pass" not in key}
    try:
        logger.info(
            f"[DEPLOY] User {user} launch deploy {name} with stack {stack_name} on squad {squad} and environment {environment}"
        )
        r.set(f"{name}-{squad}-{environment}", "Locked")
        logger.info(f"[DEPLOY] lock sld {name}-{squad}-{environment}")
        r.expire(f"{name}-{squad}-{environment}", settings.TASK_LOCKED_EXPIRED)
        logger.info(
            f"[DEPLOY] set sld {name}-{squad}-{environment} expire timeout {settings.TASK_LOCKED_EXPIRED}"
        )
        # Git clone repo
        logger.info(
            f"[DEPLOY] User {user} launch deploy {name} with stack {stack_name} on squad {squad} and environment {environment} git pull"
        )
        result = ProviderRequirements.artifact_download(
            name, stack_name, environment, squad, git_repo, branch
        )

        self.update_state(state="PULLING", meta={"done": "1 of 6"})
        if result["rc"] != 0:
            logger.error(
                f"[DEPLOY] Error when user {user} launch deploy {name} with stack {stack_name} on squad {squad} and environment {environment} git pull"
            )
            raise Exception(result)
        # Download terrafom
        logger.info(
            f"[DEPLOY] User {user} launch deploy {name} with stack {stack_name} on squad {squad} and environment {environment} download terrafom version {version}"
        )
        result = ProviderRequirements.binary_download(version)

        self.update_state(state="LOADBIN", meta={"done": "2 of 6"})
        # Delete artifactory to avoid duplicating the runner logs
        dir_path = f"/tmp/{ stack_name }/{environment}/{squad}/artifacts"
        Utils.delete_local_folder(dir_path)
        if result["rc"] != 0:
            logger.error(
                f"[DEPLOY] Error when User {user} launch deploy {name} with stack {stack_name} on squad {squad} and environment {environment} download terrafom version {version}"
            )
            raise Exception(result)

        # Create tf to use the custom backend state
        if backend_config == "":
            self.update_state(state="REMOTECONF", meta={"done": "3 of 6"})

            result = ProviderRequirements.storage_state(
                name, stack_name, environment, squad, project_path
            )
            if result["rc"] != 0:
                raise Exception(result)

        # Create tfvar serialize with json
        self.update_state(state="SETVARS", meta={"done": "4 of 6"})
        result = ProviderRequirements.parameter_vars(
            name, stack_name, environment, squad, project_path, kwargs
        )
        if result["rc"] != 0:
            raise Exception(result)
        # Plan execute
        logger.info(
            f"[DEPLOY] User {user} launch deploy {name} with stack {stack_name} on squad {squad} and environment {environment} terraform plan"
        )
        self.update_state(state="PLANNING", meta={"done": "5 of 6"})
        result = ProviderActions.plan(
            name,
            stack_name,
            branch,
            environment,
            squad,
            version,
            secreto,
            variables_file,
            project_path,
            backend_config,
        )
        # Delete artifactory to avoid duplicating the runner logs
        dir_path = f"/tmp/{ stack_name }/{environment}/{squad}/{name}/artifacts"
        Utils.delete_local_folder(dir_path)

        if result["rc"] != 0:
            logger.error(
                f"[DEPLOY] Error when User {user} launch deploy {name} with stack {stack_name} on squad {squad} and environment {environment} execute terraform plan"
            )
            raise Exception(result)
        # Apply execute
        logger.info(
            f"[DEPLOY] User {user} launch deploy {name} with stack {stack_name} on squad {squad} and environment {environment} terraform apply with timeout deploy setting {settings.DEPLOY_TMOUT}"
        )
        self.update_state(state="APPLYING", meta={"done": "6 of 6"})
        result = ProviderActions.apply(
            name,
            stack_name,
            branch,
            environment,
            squad,
            version,
            secreto,
            variables_file,
            project_path,
            backend_config,
        )
        if result["rc"] != 0:
            logger.error(
                f"[DEPLOY] Error when User {user} launch deploy {name} with stack {stack_name} on squad {squad} and environment {environment} download terrafom version {version}"
            )
            raise Exception(result)
        return result
    except Exception as err:
        if not settings.ROLLBACK:
            logger.error(
                f"[DEPLOY] Error when User {user} launch deploy {name} with stack {stack_name} on squad {squad} and environment {environment} download terrafom version {version} execute Retry"
            )
            self.retry(
                countdown=settings.TASK_RETRY_INTERVAL,
                exc=err,
                max_retries=settings.TASK_MAX_RETRY,
            )
            self.update_state(state=states.FAILURE, meta={"exc": result})
            raise Ignore()
            logger.error(
                f"[DEPLOY] Error when User {user} launch deploy {name} with stack {stack_name} on squad {squad} and environment {environment} download terrafom version {version} execute RollBack"
            )
        self.update_state(state="ROLLBACK", meta={"done": "1 of 1"})
        destroy_result = ProviderActions.destroy(
            name,
            stack_name,
            branch,
            environment,
            squad,
            version,
            secreto,
            variables_file,
            project_path,
            backend_config,
        )
        self.update_state(
            state=states.FAILURE,
            meta={
                "exc_type": type(err).__name__,
                "exc_message": traceback.format_exc().split("\n"),
            },
        )
        raise Ignore()
    finally:
        dir_path = f"/tmp/{ stack_name }/{environment}/{squad}/{name}"
        r.delete(f"{name}-{squad}-{environment}")
        if not settings.DEBUG:
            Utils.delete_local_folder(dir_path)


@celery_app.task(bind=True, acks_late=True, name="pipeline Destroy")
@push_metric()
def pipeline_destroy(
    self,
    git_repo: str,
    name: str,
    stack_name: str,
    environment: str,
    squad: str,
    branch: str,
    version: str,
    kwargs: any,
    secreto: str,
    variables_file: str = "",
    project_path: str = "",
    backend_config: str = "",
    user: str = "",
):
    filter_kwargs = {key: value for (key, value) in kwargs.items() if "pass" not in key}
    try:
        logger.info(
            f"User {user} launch destroy {name} with stack {stack_name} on squad {squad} and environment {environment}"
        )
        r.set(f"{name}-{squad}-{environment}", "Locked")
        logger.info(f"lock sld {name}-{squad}-{environment}")
        r.expire(f"{name}-{squad}-{environment}", settings.TASK_LOCKED_EXPIRED)
        logger.info(
            f"set sld {name}-{squad}-{environment} expire timeout {settings.TASK_LOCKED_EXPIRED}"
        )
        # Git clone repo
        logger.info(
            f"User {user} Destroy deploy {name} with stack {stack_name} on squad {squad} and environment {environment} git pull"
        )
        result = ProviderRequirements.artifact_download(
            name, stack_name, environment, squad, git_repo, branch
        )
        self.update_state(state="PULLING", meta={"done": "1 of 6"})
        if result["rc"] != 0:
            raise Exception(result)
        # Download terrafom
        logger.info(
            f"User {user} Destroy deploy {name} with stack {stack_name} on squad {squad} and environment {environment} download terrafom version {version}"
        )
        result = ProviderRequirements.binary_download(version)
        self.update_state(state="LOADBIN", meta={"done": "2 of 6"})
        # Delete artifactory to avoid duplicating the runner logs
        if result["rc"] != 0:
            logger.error(
                f"Error when User {user} launch destroy {name} with stack {stack_name} on squad {squad} and environment {environment} download terrafom version {version}"
            )
            raise Exception(result)
        # Create tf to use the custom backend storage state
        if backend_config == "":
            self.update_state(state="REMOTECONF", meta={"done": "3 of 6"})
            result = ProviderRequirements.storage_state(
                name, stack_name, environment, squad, project_path
            )
            if result["rc"] != 0:
                raise Exception(result)
        # Create tfvar serialize with json
        self.update_state(state="SETVARS", meta={"done": "4 of 6"})
        result = ProviderRequirements.parameter_vars(
            name, stack_name, environment, squad, project_path, kwargs
        )
        if result["rc"] != 0:
            raise Exception(result)

        logger.info(
            f"User {user} launch destroy {name} with stack {stack_name} on squad {squad} and environment {environment} execute destroy"
        )
        self.update_state(state="DESTROYING", meta={"done": "6 of 6"})
        result = ProviderActions.destroy(
            name,
            stack_name,
            branch,
            environment,
            squad,
            version,
            secreto,
            variables_file,
            project_path,
            backend_config,
        )
        if result["rc"] != 0:
            raise Exception(result)
        return result
    except Exception as err:
        self.retry(countdown=5, exc=err, max_retries=1)
        self.update_state(state=states.FAILURE, meta={"exc": result})
        raise Ignore()
    finally:
        dir_path = f"/tmp/{ stack_name }/{environment}/{squad}/{name}"
        Utils.delete_local_folder(dir_path)
        r.delete(f"{name}-{squad}-{environment}")


@celery_app.task(bind=True, acks_late=True, name="pipeline Plan")
@push_metric()
def pipeline_plan(
    self,
    git_repo: str,
    name: str,
    stack_name: str,
    environment: str,
    squad: str,
    branch: str,
    version: str,
    kwargs: any,
    secreto: str,
    variables_file: str = "",
    project_path: str = "",
    backend_config: str = "",
    user: str = "",
):
    filter_kwargs = {key: value for (key, value) in kwargs.items() if "pass" not in key}
    try:
        logger.info(
            f"User {user} launch plan {name} with stack {stack_name} on squad {squad} and environment {environment}"
        )
        self.update_state(state="GIT", meta={"done": "1 of 5"})
        result = ProviderRequirements.artifact_download(
            name, stack_name, environment, squad, git_repo, branch
        )
        if result["rc"] != 0:
            logger.error(
                f"Error when user {user} launch plan {name} with stack {stack_name} on squad {squad} and environment {environment} git pull"
            )
            raise Exception(result)
        self.update_state(state="BINARY", meta={"done": "2 of 5"})
        logger.info(
            f"User {user} launch plan {name} with stack {stack_name} on squad {squad} and environment {environment} download terrafom version {version}"
        )
        result = ProviderRequirements.binary_download(version)
        dir_path = f"/tmp/{ stack_name }/{environment}/{squad}/artifacts"
        Utils.delete_local_folder(dir_path)
        if result["rc"] != 0:
            logger.error(
                f"Error when User {user} launch plan {name} with stack {stack_name} on squad {squad} and environment {environment} download terrafom version {version}"
            )
            raise Exception(result)
        
        if backend_config == "":
            self.update_state(state="REMOTE", meta={"done": "3 of 5"})
            result = ProviderRequirements.storage_state(
                name, stack_name, environment, squad, project_path
            )
            if result["rc"] != 0:
                raise Exception(result)

        self.update_state(state="VARS", meta={"done": "4 of 5"})
        result = ProviderRequirements.parameter_vars(
            name, stack_name, environment, squad, project_path, kwargs
        )
        if result["rc"] != 0:
            raise Exception(result)

        self.update_state(state="PLAN", meta={"done": "5 of 5"})
        result = ProviderActions.plan(
            name,
            stack_name,
            branch,
            environment,
            squad,
            version,
            secreto,
            variables_file,
            project_path,
            backend_config,
        )
        dir_path = f"/tmp/{ stack_name }/{environment}/{squad}/{name}/artifacts"
        Utils.delete_local_folder(dir_path)
        if result["rc"] != 0:
            logger.error(
                f"Error when User {user} launch plan {name} with stack {stack_name} on squad {squad} and environment {environment} execute terraform plan"
            )
            raise Exception(result)
        return result
    except Exception as err:
        self.retry(countdown=5, exc=err, max_retries=1)
        self.update_state(state=states.FAILURE, meta={"exc": result})
        raise Ignore()
    finally:
        dir_path = f"/tmp/{ stack_name }/{environment}/{squad}/{name}"
        Utils.delete_local_folder(dir_path)


@celery_app.task(
    bind=True, acks_late=True, time_limit=settings.GIT_TMOUT, name="pipeline git pull"
)
def pipeline_git_pull(
    self,
    git_repo: str,
    name: str,
    stack_name: str,
    environment: str,
    squad: str,
    branch: str,
    project_path: str,
):
    try:
        git_result = ProviderRequirements.artifact_download(
            name, stack_name, environment, squad, git_repo, branch, project_path
        )
        if git_result["rc"] != 0:
            raise Exception(git_result.get("stdout"))

        self.update_state(state="GET_VARS_AS_JSON", meta={"done": "2 of 2"})
        result = ProviderGetVars.json_vars(
            environment=environment, stack_name=stack_name, squad=squad, name=name, project_path=project_path
        )
        if result["rc"] != 0:
            raise Exception(result.get("stdout"))
        result["tfvars"] = git_result["tfvars"]
        return result
    except Exception as err:
        self.retry(
            countdown=1, exc=err, max_retries=settings.TASK_MAX_RETRY
        )
        self.update_state(state=states.FAILURE, meta={"exc": result})
        raise Ignore()
    finally:
        dir_path = f"/tmp/{stack_name}/{environment}/{squad}/{name}"
        Utils.delete_local_folder(dir_path)


@celery_app.task(
    bind=True, acks_late=True, time_limit=settings.GIT_TMOUT, name="download git repo"
)
def git(
    self,
    git_repo: str,
    name: str,
    stack_name: str,
    environment: str,
    squad: str,
    branch: str,
):
    try:
        result = ProviderRequirements.artifact_download(
            name, stack_name, environment, squad, git_repo, branch
        )
    except Exception as err:
        self.retry(
            countdown=settings.GIT_TMOUT, exc=err, max_retries=settings.TASK_MAX_RETRY
        )
        self.update_state(state=states.FAILURE, meta={"exc": result})
        raise Ignore()
    return stack_name, environment, squad, name, result


@celery_app.task(
    bind=True,
    acks_late=True,
    time_limit=settings.WORKER_TMOUT,
    max_retries=1,
    name="terraform output",
)
def output(self, stack_name: str, squad: str, environment: str, name: str):
    try:
        output_result = ProviderActions.output(stack_name, squad, environment, name)
        return output_result
    except Exception as err:
        return {"stdout": err}
    finally:
        dir_path = f"/tmp/artifacts"
        Utils.delete_local_folder(dir_path)


@celery_app.task(
    bind=True,
    acks_late=True,
    time_limit=settings.WORKER_TMOUT,
    max_retries=1,
    name="terraform unlock",
)
def unlock(self, stack_name: str, squad: str, environment: str, name: str):
    try:
        unlock_result = ProviderActions.unlock(stack_name, squad, environment, name)
        return unlock_result
    except Exception as err:
        return {"stdout": err}


@celery_app.task(
    bind=True, acks_late=True, time_limit=settings.WORKER_TMOUT, name="terraform show"
)
def show(self, stack_name: str, squad: str, environment: str, name: str):
    show_result = ProviderActions.show(stack_name, squad, environment, name)
    return show_result


@celery_app.task(
    bind=True, acks_late=True, time_limit=settings.WORKER_TMOUT, name="schedules list"
)
def schedules_list(self):
    try:
        return request_url(verb="GET", uri=f"schedules/").get("json")
    except Exception:
        pass


@celery_app.task(
    bind=True, acks_late=True, time_limit=settings.WORKER_TMOUT, name="schedule get"
)
def schedule_get(self, deploy_name: str):
    try:
        return request_url(verb="GET", uri=f"schedule/{deploy_name}").get("json")
    except Exception:
        pass


@celery_app.task(
    bind=True, acks_late=True, time_limit=settings.WORKER_TMOUT, name="schedule remove"
)
def schedule_delete(self, deploy_name: str):
    try:
        return request_url(verb="DELETE", uri=f"schedule/{deploy_name}").get("json")
    except Exception:
        pass


@celery_app.task(
    bind=True, acks_late=True, time_limit=settings.WORKER_TMOUT, name="schedule add"
)
def schedule_add(self, deploy_name: str):
    try:
        return request_url(verb="POST", uri=f"schedule/{deploy_name}").get("json")
    except Exception as err:
        return err


@celery_app.task(
    bind=True,
    acks_late=True,
    time_limit=settings.WORKER_TMOUT,
    max_retries=1,
    name="Update schedule",
)
def schedule_update(self, deploy_name: str):
    try:
        request_url(verb="DELETE", uri=f"schedule/{deploy_name}")
        return request_url(verb="POST", uri=f"schedule/{deploy_name}").get("json")
    except Exception as err:
        logging.warning(request_url(verb="POST", uri=f"schedule/{deploy_name}"))
        return err
