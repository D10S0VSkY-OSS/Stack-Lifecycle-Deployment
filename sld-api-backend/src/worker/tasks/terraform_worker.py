import logging
import redis
from celery import states
from celery.exceptions import Ignore
from celery.utils.log import get_task_logger
from config.api import settings
from config.celery_config import celery_app
from src.worker.domain.entities.worker import DeployParams, DownloadGitRepoParams
from src.worker.domain.services.pipeline import Pipeline

from src.worker.domain.services.provider import ProviderActions
from src.worker.tasks.helpers.folders import Utils
from src.worker.tasks.helpers.metrics import push_metric
from src.worker.tasks.helpers.schedule import request_url

r = redis.Redis(
    host=settings.CACHE_SERVER,
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
    params: DeployParams,

):
    try:
        params["task_id"] = self.request.id
        params = DeployParams(**params)
        pipeline = Pipeline(params=params)
        pipeline.locked_task()
        self.update_state(state="PULLING", meta={"done": "1 of 6"})
        pipeline.download_git_repo()
        self.update_state(state="LOADBIN", meta={"done": "2 of 6"})
        pipeline.download_binary()
        self.update_state(state="REMOTECONF", meta={"done": "3 of 6"})
        pipeline.set_remote_state()
        self.update_state(state="SETVARS", meta={"done": "4 of 6"})
        pipeline.set_tfvars()
        self.update_state(state="PLANNING", meta={"done": "5 of 6"})
        pipeline.execute_plan()
        self.update_state(state="APPLYING", meta={"done": "6 of 6"})
        apply_result = pipeline.execute_apply()
        return apply_result
    except Exception as err:
        self.retry(
            countdown=settings.TASK_RETRY_INTERVAL,
            exc=err,
            max_retries=settings.TASK_MAX_RETRY,
        )
        self.update_state(state=states.FAILURE, meta={"exc": apply_result})
        raise Ignore()
    finally:
        dir_path = f"/tmp/{params.stack_name}/{params.environment}/{params.squad}/{params.name}"
        pipeline.unlock_task()
        if not settings.DEBUG:
            Utils.delete_local_folder(dir_path)


@celery_app.task(bind=True, acks_late=True, name="pipeline Destroy")
@push_metric()
def pipeline_destroy(
    self,
    params: DeployParams,
):
    try:
        params["task_id"] = self.request.id
        params = DeployParams(**params)
        pipeline = Pipeline(params=params)
        pipeline.locked_task()
        self.update_state(state="PULLING", meta={"done": "1 of 5"})
        pipeline.download_git_repo()
        self.update_state(state="LOADBIN", meta={"done": "2 of 5"})
        pipeline.download_binary()
        self.update_state(state="REMOTECONF", meta={"done": "3 of 5"})
        pipeline.set_remote_state()
        self.update_state(state="SETVARS", meta={"done": "4 of 5"})
        pipeline.set_tfvars()
        self.update_state(state="DESTROYING", meta={"done": "5 of 5"})
        destroy_result = pipeline.execute_destroy()
        if destroy_result["rc"] != 0:
            raise Exception(destroy_result)
        return destroy_result
    except Exception as err:
        self.retry(countdown=5, exc=err, max_retries=1)
        self.update_state(state=states.FAILURE, meta={"exc": destroy_result})
        raise Ignore()
    finally:
        dir_path = f"/tmp/{ params.stack_name }/{ params.environment}/{ params.squad}/{ params.name}"
        Utils.delete_local_folder(dir_path)
        pipeline.unlock_task()


@celery_app.task(bind=True, acks_late=True, name="pipeline Plan")
@push_metric()
def pipeline_plan(
    self,
    params: DeployParams,
):
    try:
        params["task_id"] = self.request.id
        params = DeployParams(**params)
        pipeline = Pipeline(params=params)
        pipeline.locked_task()
        self.update_state(state="PULLING", meta={"done": "1 of 5"})
        pipeline.download_git_repo()
        self.update_state(state="LOADBIN", meta={"done": "2 of 5"})
        pipeline.download_binary()
        self.update_state(state="REMOTECONF", meta={"done": "3 of 5"})
        pipeline.set_remote_state()
        self.update_state(state="SETVARS", meta={"done": "4 of 5"})
        pipeline.set_tfvars()
        self.update_state(state="PLANNING", meta={"done": "5 of 5"})
        plan_result = pipeline.execute_plan()
        return plan_result
    except Exception as err:
        self.retry(
            countdown=settings.TASK_RETRY_INTERVAL,
            exc=err,
            max_retries=settings.TASK_MAX_RETRY,
        )
        self.update_state(state=states.FAILURE, meta={"exc": plan_result})
        raise Ignore()
    finally:
        dir_path = f"/tmp/{params.stack_name}/{params.environment}/{params.squad}/{params.name}"
        pipeline.unlock_task()
        if not settings.DEBUG:
            Utils.delete_local_folder(dir_path)


@celery_app.task(
    bind=True, acks_late=True, time_limit=settings.GIT_TMOUT, name="pipeline git pull"
)
def pipeline_git_pull(
    self,
    params: DownloadGitRepoParams,
):
    try:
        params = DownloadGitRepoParams(**params)
        pipeline = Pipeline(params=params)
        self.update_state(state="PULLING", meta={"done": "1 of 2"})
        git_result = pipeline.download_git_repo()
        if git_result["rc"] != 0:
            raise Exception(git_result.get("stdout"))

        self.update_state(state="GET_VARS_AS_JSON", meta={"done": "2 of 2"})
        get_vars_result = pipeline.get_variables()
        if get_vars_result["rc"] != 0:
            raise Exception(get_vars_result.get("stdout"))
        get_vars_result["tfvars"] = git_result["tfvars"]
        return get_vars_result
    except Exception as err:
        self.retry(countdown=1, exc=err, max_retries=settings.TASK_MAX_RETRY)
        self.update_state(state=states.FAILURE, meta={"exc": get_vars_result})
        raise Ignore()
    finally:
        dir_path = f"/tmp/{ params.stack_name }/{params.environment}/{params.squad}/{params.name}"
        Utils.delete_local_folder(dir_path)


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
