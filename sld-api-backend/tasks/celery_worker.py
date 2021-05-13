from config.celery_config import celery_app
from celery import states
from celery.exceptions import Ignore
import traceback
from core.providers.terraform import TerraformActions as tf
from helpers.schedule import request_url
from config.api import settings


@celery_app.task(bind=True, acks_late=True, time_limit=7200, name='pipelineDeploy')
def pipelineDeploy(self, git_repo, name, stack_name, environment, squad, branch, version, kwargs, secreto):
    filter_kwargs = {key:value for (key,value) in kwargs.items() if "pass" not in key}
    print(git_repo, name, stack_name, environment,
          squad, branch, version, filter_kwargs)
    try:
        # Git clone repo
        result = tf.gitClone(git_repo, name, stack_name,
                             environment, squad, branch)
        self.update_state(state='PULLING', meta={'done': "1 of 6"})
        if result['rc'] != 0:
            raise Exception(result)
        # Download terrafom
        result = tf.binaryDownload(stack_name, environment, squad, version)
        self.update_state(state='LOADBIN', meta={'done': "2 of 6"})
        # Delete artifactory to avoid duplicating the runner logs
        dir_path = f"/tmp/{ stack_name }/{environment}/{squad}/artifacts"
        tf.deleteLocalFolder(dir_path)
        if result['rc'] != 0:
            raise Exception(result)
        # Create tf to use the custom artifactory as config
        self.update_state(state='REMOTECONF', meta={'done': "3 of 6"})
        result = tf.tftstateRender(stack_name, environment, squad, name)
        if result['rc'] != 0:
            raise Exception(result)
        # Create tfvar serialize with json
        self.update_state(state='SETVARS', meta={'done': "4 of 6"})
        result = tf.tfvars(stack_name, environment, squad, name, vars=kwargs)
        if result['rc'] != 0:
            raise Exception(result)
        # Plan execute
        self.update_state(state='PLANNING', meta={'done': "5 of 6"})
        result = tf.planExcute(stack_name, environment,
                               squad, name, version, data=secreto)
        # Delete artifactory to avoid duplicating the runner logs
        dir_path = f"/tmp/{ stack_name }/{environment}/{squad}/{name}/artifacts"
        tf.deleteLocalFolder(dir_path)
        if result['rc'] != 0:
            raise Exception(result)
        # Apply execute
        self.update_state(state='APPLYING', meta={'done': "6 of 6"})
        result = tf.applyExecute(
            stack_name, environment, squad, name, version, data=secreto)
        if result['rc'] != 0:
            raise Exception(result)
        return result
    except Exception as err:
        if not settings.ROLLBACK:
            self.retry(countdown=settings.TASK_RETRY_INTERVAL,
                       exc=err, max_retries=settings.TASK_MAX_RETRY)
            self.update_state(state=states.FAILURE, meta={'exc': result})
            raise Ignore()
        self.update_state(state="ROLLBACK", meta={'done': "1 of 1"})
        destroy_eresult = tf.destroyExecute(
            stack_name, environment, squad, name, version, data=secreto)
        self.update_state(state=states.FAILURE, meta={
            'exc_type': type(err).__name__,
            'exc_message': traceback.format_exc().split('\n')
            })
        raise Ignore()
    finally:
        dir_path = f"/tmp/{ stack_name }/{environment}/{squad}/{name}"
        if not settings.DEBUG:
            tf.deleteLocalFolder(dir_path)
        try:
            print(request_url(verb='DELETE', uri=f'schedule/{name}'))
            print(request_url(verb='POST', uri=f'schedule/{name}'))
        except Exception as err:
            print(err)
            pass


@celery_app.task(bind=True, acks_late=True, name='pipelineDestroy')
def pipelineDestroy(self, git_repo, name, stack_name, environment, squad, branch, version, kwargs, secreto):
    filter_kwargs = {key:value for (key,value) in kwargs.items() if "pass" not in key}
    print(git_repo, name, stack_name, environment,
          squad, branch, version, filter_kwargs)
    try:
        # Git clone repo
        result = tf.gitClone(git_repo, name, stack_name,
                             environment, squad, branch)
        self.update_state(state='PULLING', meta={'done': "1 of 6"})
        if result['rc'] != 0:
            raise Exception(result)
        # Download terrafom
        result = tf.binaryDownload(stack_name, environment, squad, version)
        self.update_state(state='LOADBIN', meta={'done': "2 of 6"})
        # Delete artifactory to avoid duplicating the runner logs
        dir_path = f"/tmp/{ stack_name }/{environment}/{squad}/artifacts"
        tf.deleteLocalFolder(dir_path)
        if result['rc'] != 0:
            raise Exception(result)
        # Create tf to use the custom artifactory as config
        self.update_state(state='REMOTECONF', meta={'done': "3 of 6"})
        result = tf.tftstateRender(stack_name, environment, squad, name)
        if result['rc'] != 0:
            raise Exception(result)
        # Create tfvar serialize with json
        self.update_state(state='SETVARS', meta={'done': "4 of 6"})
        result = tf.tfvars(stack_name, environment, squad, name, vars=kwargs)
        if result['rc'] != 0:
            raise Exception(result)

        self.update_state(state='DESTROYING', meta={'done': "6 of 6"})
        result = tf.destroyExecute(
            stack_name, environment, squad, name, version, data=secreto)
        if result['rc'] != 0:
            raise Exception(result)
        return result
    except Exception as err:
        self.retry(countdown=5, exc=err, max_retries=1)
        self.update_state(state=states.FAILURE, meta={'exc': result})
        raise Ignore()
    finally:
        dir_path = f"/tmp/{ stack_name }/{environment}/{squad}/{name}"
        tf.deleteLocalFolder(dir_path)


@celery_app.task(bind=True, acks_late=True, name='pipelinePlan')
def pipelinePlan(self, git_repo, name, stack_name, environment, squad, branch, version, kwargs, secreto):
    filter_kwargs = {key:value for (key,value) in kwargs.items() if "pass" not in key}
    print(git_repo, name, stack_name, environment,
          squad, branch, version, filter_kwargs)
    try:
        self.update_state(state='GIT', meta={'done': "1 of 5"})
        result = tf.gitClone(git_repo, name, stack_name,
                             environment, squad, branch)
        if result['rc'] != 0:
            raise Exception(result)

        self.update_state(state='BINARY', meta={'done': "2 of 5"})
        result = tf.binaryDownload(stack_name, environment, squad, version)
        dir_path = f"/tmp/{ stack_name }/{environment}/{squad}/artifacts"
        tf.deleteLocalFolder(dir_path)
        if result['rc'] != 0:
            raise Exception(result)

        self.update_state(state='REMOTE', meta={'done': "3 of 5"})
        result = tf.tftstateRender(stack_name, environment, squad, name)
        if result['rc'] != 0:
            raise Exception(result)

        self.update_state(state='VARS', meta={'done': "4 of 5"})
        result = tf.tfvars(stack_name, environment, squad, name, vars=kwargs)
        if result['rc'] != 0:
            raise Exception(result)

        self.update_state(state='PLAN', meta={'done': "5 of 5"})
        result = tf.planExcute(stack_name, environment,
                               squad, name, version, data=secreto)
        dir_path = f"/tmp/{ stack_name }/{environment}/{squad}/{name}/artifacts"
        tf.deleteLocalFolder(dir_path)
        if result['rc'] != 0:
            raise Exception(result)
        return result
    except Exception as err:
        self.retry(countdown=5, exc=err, max_retries=1)
        self.update_state(state=states.FAILURE, meta={'exc': result})
        raise Ignore()
    finally:
        dir_path = f"/tmp/{ stack_name }/{environment}/{squad}/{name}"
        tf.deleteLocalFolder(dir_path)


@celery_app.task(bind=True,
                 acks_late=True,
                 time_limit=60,
                 name='download git repo')
def git(self, git_repo, name, stack_name, environment, squad, branch):
    try:
        result = tf.gitClone(git_repo, name, stack_name,
                             environment, squad, branch)
    except Exception as err:
        raise err
    return stack_name, environment, squad, name, result


@celery_app.task(bind=True, acks_late=True, time_limit=300, max_retries=1, name='terraform output')
def output(self, stack_name, environment, squad, name):
    try:
        output_result = tf.outputExecute(
            stack_name, environment, squad, name)
        return output_result
    except Exception as err:
        return {"stdout": err}


@celery_app.task(bind=True, acks_late=True, time_limit=300, max_retries=1, name='terraform unlock')
def unlock(self, stack_name, environment, squad, name):
    try:
        unlock_result = tf.UnlockExecute(
            stack_name, environment, squad, name)
        return unlock_result
    except Exception as err:
        return {"stdout": err}


@celery_app.task(bind=True, acks_late=True, time_limit=300, name='terraform show')
def show(self, stack_name, environment, squad, name):
    show_result = tf.showExecute(
        stack_name, environment, squad, name)
    return show_result


@celery_app.task(bind=True, acks_late=True, time_limit=300, name='schedules list')
def schedules_list(self):
    try:
        return request_url(verb='GET', uri=f'schedules/')
    except Exception as err:
        pass

@celery_app.task(bind=True, acks_late=True, time_limit=300, name='schedule get')
def schedule_get(self, deploy_name):
    try:
        return request_url(verb='GET', uri=f'schedule/{deploy_name}')
    except Exception as err:
        pass

@celery_app.task(bind=True, acks_late=True, time_limit=300, name='schedule remove')
def schedule_delete(self, deploy_name):
    try:
        return request_url(verb='DELETE', uri=f'schedule/{deploy_name}')
    except Exception as err:
        pass


@celery_app.task(bind=True, acks_late=True, time_limit=300, name='schedule add')
def schedule_add(self, deploy_name):
    try:
        return request_url(verb='POST', uri=f'schedule/{deploy_name}')
    except Exception as err:
        return err


@celery_app.task(bind=True, acks_late=True, name='delete local module stack ')
def delete_local_stack(self, environment, squad, args):
    result = tf.deleteLocalRepo(environment, squad, args)
    return result


@celery_app.task(bind=True, acks_late=True, name='get variables list')
def get_variable_list(self, environment, stack_name, squad, name):
    result = tf.getVarsList(environment, stack_name, squad, name)
    return result


@celery_app.task(bind=True, acks_late=True, name='get variables json')
def get_variable_json(self, environment, stack_name, squad, name):
    result = tf.getVarsJson(environment, stack_name, squad, name)
    return result


@celery_app.task(bind=True, acks_late=True, name='get variables from tfvars')
def get_tfvars(self, environment, stack_name, squad, name):
    result = tf.getVarsTfvars(environment, stack_name, squad, name)
    return result
