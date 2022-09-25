import logging
import traceback

import redis
from celery import states
from celery.exceptions import Ignore
from celery.utils.log import get_task_logger
from config.api import settings
from config.celery_config import celery_app
from core.providers.sld import Providers, Terraform
from core.providers.terraform import TerraformRequirements
from core.providers.terraform import TerraformGetVars
from core.providers.terraform import TerraformUtils
from core.providers.terraform import TerraformActions
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

terrafom = Terraform()
provider = Providers(terrafom)


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
        result = TerraformRequirements.artifactoryFunction(
            name,
            stack_name,
            environment, 
            squad, 
            git_repo, 
            branch
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
        result = TerraformRequirements.binaryFunction(version)

        self.update_state(state="LOADBIN", meta={"done": "2 of 6"})
        # Delete artifactory to avoid duplicating the runner logs
        dir_path = f"/tmp/{ stack_name }/{environment}/{squad}/artifacts"
        TerraformUtils.delete_local_folder(dir_path)
        if result["rc"] != 0:
            logger.error(
                f"[DEPLOY] Error when User {user} launch deploy {name} with stack {stack_name} on squad {squad} and environment {environment} download terrafom version {version}"
            )
            raise Exception(result)

        # Create tf to use the custom artifactory as config
        self.update_state(state="REMOTECONF", meta={"done": "3 of 6"})

        result = TerraformRequirements.storageState(
            name,
            stack_name,
            environment, 
            squad, 
            project_path
            )
        if result["rc"] != 0:
            raise Exception(result)

        # Create tfvar serialize with json
        self.update_state(state="SETVARS", meta={"done": "4 of 6"})
        result = TerraformRequirements.parameterVars(
            name,
            stack_name,
            environment, 
            squad, 
            project_path,
            kwargs
            )
        if result["rc"] != 0:
            raise Exception(result)
        # Plan execute
        logger.info(
            f"[DEPLOY] User {user} launch deploy {name} with stack {stack_name} on squad {squad} and environment {environment} terraform plan"
        )
        self.update_state(state="PLANNING", meta={"done": "5 of 6"})
        result = provider.execute(
            TerraformActions.plan_execute(
                stack_name,
                environment,
                squad,
                name,
                version,
                variables_file,
                project_path,
                data=secreto,
            )
        )
        # Delete artifactory to avoid duplicating the runner logs
        dir_path = f"/tmp/{ stack_name }/{environment}/{squad}/{name}/artifacts"
        provider.execute(TerraformUtils.delete_local_folder(dir_path))

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
        result = provider.execute(
            TerraformActions.apply_execute(
                stack_name,
                branch,
                environment,
                squad,
                name,
                version,
                variables_file,
                project_path,
                data=secreto,
            )
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
        destroy_result = TerraformActions.destroy_execute(
            stack_name,
            branch,
            environment,
            squad,
            name,
            version,
            variables_file,
            project_path,
            data=secreto,
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
            TerraformUtils.delete_local_folder(dir_path)


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
        result = TerraformRequirements.git_clone(git_repo, name, stack_name, environment, squad, branch)
        self.update_state(state="PULLING", meta={"done": "1 of 6"})
        if result["rc"] != 0:
            raise Exception(result)
        # Download terrafom
        logger.info(
            f"User {user} Destroy deploy {name} with stack {stack_name} on squad {squad} and environment {environment} download terrafom version {version}"
        )
        result = TerraformRequirements.binary_download(stack_name, environment, squad, version)
        self.update_state(state="LOADBIN", meta={"done": "2 of 6"})
        # Delete artifactory to avoid duplicating the runner logs
        if result["rc"] != 0:
            logger.error(
                f"Error when User {user} launch destroy {name} with stack {stack_name} on squad {squad} and environment {environment} download terrafom version {version}"
            )
            raise Exception(result)
        # Create tf to use the custom artifactory as config
        self.update_state(state="REMOTECONF", meta={"done": "3 of 6"})
        result = TerraformRequirements.tfstate_render(stack_name, environment, squad, project_path, name)
        if result["rc"] != 0:
            raise Exception(result)
        # Create tfvar serialize with json
        self.update_state(state="SETVARS", meta={"done": "4 of 6"})
        result = TerraformRequirements.tfvars(
            stack_name, environment, squad, name, project_path, vars=kwargs
        )
        if result["rc"] != 0:
            raise Exception(result)

        logger.info(
            f"User {user} launch destroy {name} with stack {stack_name} on squad {squad} and environment {environment} execute destroy"
        )
        self.update_state(state="DESTROYING", meta={"done": "6 of 6"})
        result = TerraformActions.destroy_execute(
            stack_name,
            branch,
            environment,
            squad,
            name,
            version,
            variables_file,
            project_path,
            data=secreto,
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
        TerraformUtils.delete_local_folder(dir_path)
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
    user: str = "",
):
    filter_kwargs = {key: value for (key, value) in kwargs.items() if "pass" not in key}
    try:
        logger.info(
            f"User {user} launch plan {name} with stack {stack_name} on squad {squad} and environment {environment}"
        )
        self.update_state(state="GIT", meta={"done": "1 of 5"})
        result = TerraformRequirements.git_clone(git_repo, name, stack_name, environment, squad, branch)
        if result["rc"] != 0:
            logger.error(
                f"Error when user {user} launch plan {name} with stack {stack_name} on squad {squad} and environment {environment} git pull"
            )
            raise Exception(result)
        self.update_state(state="BINARY", meta={"done": "2 of 5"})
        logger.info(
            f"User {user} launch plan {name} with stack {stack_name} on squad {squad} and environment {environment} download terrafom version {version}"
        )
        result = TerraformRequirements.binary_download(stack_name, environment, squad, version)
        dir_path = f"/tmp/{ stack_name }/{environment}/{squad}/artifacts"
        TerraformUtils.delete_local_folder(dir_path)
        if result["rc"] != 0:
            logger.error(
                f"Error when User {user} launch plan {name} with stack {stack_name} on squad {squad} and environment {environment} download terrafom version {version}"
            )
            raise Exception(result)

        self.update_state(state="REMOTE", meta={"done": "3 of 5"})
        result = TerraformRequirements.tfstate_render(stack_name, environment, squad, project_path, name)
        if result["rc"] != 0:
            raise Exception(result)

        self.update_state(state="VARS", meta={"done": "4 of 5"})
        result = TerraformRequirements.tfvars(
            stack_name, environment, squad, name, project_path, vars=kwargs
        )
        if result["rc"] != 0:
            raise Exception(result)

        self.update_state(state="PLAN", meta={"done": "5 of 5"})
        result = TerraformActions.plan_execute(
            stack_name,
            environment,
            squad,
            name,
            version,
            variables_file,
            project_path,
            data=secreto,
        )
        dir_path = f"/tmp/{ stack_name }/{environment}/{squad}/{name}/artifacts"
        TerraformUtils.delete_local_folder(dir_path)
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
        TerraformUtils.delete_local_folder(dir_path)


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
):
    try:
        git_result = TerraformRequirements.git_clone(
            git_repo, name, stack_name, environment, squad, branch
        )
        if git_result["rc"] != 0:
            raise Exception(result.get("stdout"))

        self.update_state(state="GET_VARS_AS_JSON", meta={"done": "2 of 2"})
        result = TerraformGetVars.get_vars_json(
            environment=environment, stack_name=stack_name, squad=squad, name=name
        )
        if result["rc"] != 0:
            raise Exception(result)
        result["tfvars"] = git_result["tfvars"]
        return result
    except Exception as err:
        self.retry(
            countdown=settings.GIT_TMOUT, exc=err, max_retries=settings.TASK_MAX_RETRY
        )
        self.update_state(state=states.FAILURE, meta={"exc": result})
        raise Ignore()
    finally:
        dir_path = f"/tmp/artifacts"
        TerraformUtils.delete_local_folder(dir_path)


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
        result = TerraformRequirements.git_clone(git_repo, name, stack_name, environment, squad, branch)
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
def output(self, stack_name: str, environment: str, squad: str, name: str):
    try:
        output_result = TerraformActions.output_execute(stack_name, environment, squad, name)
        return output_result
    except Exception as err:
        return {"stdout": err}
    finally:
        dir_path = f"/tmp/artifacts"
        TerraformUtils.delete_local_folder(dir_path)


@celery_app.task(
    bind=True,
    acks_late=True,
    time_limit=settings.WORKER_TMOUT,
    max_retries=1,
    name="terraform unlock",
)
def unlock(self, stack_name: str, environment: str, squad: str, name: str):
    try:
        unlock_result = TerraformActions.unlock_execute(stack_name, environment, squad, name)
        return unlock_result
    except Exception as err:
        return {"stdout": err}


@celery_app.task(
    bind=True, acks_late=True, time_limit=settings.WORKER_TMOUT, name="terraform show"
)
def show(self, stack_name: str, environment: str, squad: str, name: str):
    show_result = TerraformActions.show_execute(stack_name, environment, squad, name)
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


@celery_app.task(bind=True, acks_late=True, name="delete local module stack ")
def delete_local_stack(self, environment: str, squad: str, args: any):
    result = tf.delete_local_repo(environment, squad, args)
    return result


@celery_app.task(bind=True, acks_late=True, name="get variables list")
def get_variable_list(self, environment: str, stack_name: str, squad: str, name: str):
    result = TerraformGetVars.get_vars_list(environment, stack_name, squad, name)
    return result


@celery_app.task(bind=True, acks_late=True, name="get variables json")
def get_variable_json(self, environment: str, stack_name: str, squad: str, name: str):
    result = TerraformGetVars.get_vars_json(environment, stack_name, squad, name)
    return result


@celery_app.task(bind=True, acks_late=True, name="get variables from tfvars")
def get_tfvars(self, environment: str, stack_name: str, squad: str, name: str):
    result = TerraformGetVars.get_vars_tfvars(environment, stack_name, squad, name)
    return result
