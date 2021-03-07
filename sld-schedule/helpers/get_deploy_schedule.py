from fastapi import HTTPException
from helpers.api_request import request_url
from helpers.api_token import get_token
from config.api import settings
import jmespath
import time
import json
import logging


from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler


logging.basicConfig(
    format='%(levelname)-8s  %(message)s',
    level=logging.INFO,
)
scheduler = BackgroundScheduler()


def init_check_schedule():
    try:
        count=1000
        for i in range(count):
            count -=1
            logging.warning(f"Can't validate in the api-backend, Set user and password bot in api-backend try {count} of 100")
            time.sleep(3)
            token = get_token(settings.CREDENTIALS_BOT)
            response = request_url(verb='GET',uri=f'deploy/',headers={"Authorization": f"Bearer {token}"})
            if response.get("status_code") == 200:
                break

        if response.get("status_code") != 200:
            raise Exception(response)
        data_json = response.get('json')
        deploy_list = jmespath.search('[*].name', data_json)

        for i in deploy_list:
            addDeployToSchedule(i)
    except Exception as err:
        raise err


def get_deploy_by_id(deploy_id):
    token = get_token(settings.CREDENTIALS_BOT)
    try:
        response = request_url(verb='GET',
                               uri=f'deploy/{deploy_id}',
                               headers={"Authorization": f"Bearer {token}"})
        if response.get("status_code") != 200:
            raise Exception(response)
        logging.info(
            f'Get deploy by id {deploy_id} - {response.get("status_code")} - {response.get("json").get("squad")} - {response.get("json").get("name")}')
        data = {
            "deploy_id": deploy_id,
            "name": response['json']['name'],
            "start": response['json']['start_time'],
            "destroy": response['json']['destroy_time'],
        }
        return(data)
    except Exception as err:
        raise HTTPException(
            status_code=404,
            detail=f"{err}")


def update_deploy(deploy_id):
    token = get_token(settings.CREDENTIALS_BOT)
    endpoint = f'deploy/{deploy_id}'
    response = request_url(verb='GET', uri=f'{endpoint}', headers={
                           "Authorization": f"Bearer {token}"})
    logging.info(
        f'Get deploy info by id {deploy_id} - {response["status_code"]}')
    content = response.get('json')
    data = {
        "start_time": content['start_time'],
        "destroy_time": content['destroy_time'],
        "variables": content['variables']
    }
    response = request_url(
        verb='PATCH',
        uri=f'master/deploy/{content.get("id")}',
        headers={
            "Authorization": f"Bearer {token}"},
        json=data)
    logging.info(
        f'Update deploy info by id {deploy_id} - {response["status_code"]}')


def destroy_deploy(deploy_id):
    token = get_token(settings.CREDENTIALS_BOT)
    endpoint = f'deploy/{deploy_id}'
    response = request_url(verb='GET', uri=f'{endpoint}', headers={
                           "Authorization": f"Bearer {token}"})
    content = response.get('json')
    logging.info(
        f'Get deploy info by id {deploy_id} - {response["status_code"]}')
    data = {
        "start_time": content['start_time'],
        "destroy_time": content['destroy_time'],
        "variables": content['variables']
    }
    response = request_url(
        verb='PUT',
        uri=f'master/deploy/{content.get("id")}',
        headers={
            "Authorization": f"Bearer {token}"},
        json=data)
    logging.info(
        f'Destroy deploy info by id {deploy_id} - {response["status_code"]}')


def getJob(deploy_id):
    logging.info(f'Get job {deploy_id}')
    start = scheduler.get_job(str(f'start-{deploy_id}'))
    destroy = scheduler.get_job(str(f'destroy-{deploy_id}'))
    return start, destroy


def getJobs():
    logging.info(f'Get job all jobs')
    return scheduler.get_jobs()


def removeJob(deploy_id):
    logging.info(f'Remove job {deploy_id}')
    try:
        scheduler.remove_job(f'start-{deploy_id}')
        scheduler.remove_job(f'destroy-{deploy_id}')
        return {deploy_id: "removed"}
    except Exception as err:
        return err


def add_job(func, job_name: str, job_id: str, start_time: str = None):
    # Add start job to scheduler state pending
    if not start_time:
        return None
    scheduler.add_job(
        func,
        CronTrigger.from_crontab(
            start_time
        ),
        id=str(f'start-{job_id}'),
        name=f'start-{job_name}',
        args=[job_id]
    )
    # Start job
    try:
        scheduler.start()
    except Exception as err:
        pass
    start = scheduler.get_job(str(f'start-{job_id}'))
    return start


def destroy_job(func, job_name: str, job_id: str, destroy_time: str = None,):
    # Add start job to scheduler state pending
    if not destroy_time:
        return None
    scheduler.add_job(
        func,
        CronTrigger.from_crontab(
            destroy_time
        ),
        id=str(f'destroy-{job_id}'),
        name=f'destroy-{job_name}',
        args=[job_id]
    )
    # Start job
    try:
        scheduler.start()
    except Exception as err:
        pass
    destroy = scheduler.get_job(str(f'destroy-{job_id}'))
    return destroy


def addDeployToSchedule(deploy_id: int):
    # Get data by deploy_id
    data = get_deploy_by_id(deploy_id)
    name = data['name']
    start_time = data['start']
    destroy_time = data['destroy']
    # Add start job to scheduler state pending
    update = add_job(
        func=update_deploy,
        start_time=start_time,
        job_name=name,
        job_id=deploy_id
    )
    destroy = destroy_job(
        func=destroy_deploy,
        destroy_time=destroy_time,
        job_name=name,
        job_id=deploy_id
    )
    logging.info(f'Deploy deploy info {update}')
    logging.info(f'Destroy deploy info {destroy}')
    return update, destroy
