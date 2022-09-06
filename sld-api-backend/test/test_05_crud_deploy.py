import time

from config.api import settings
from helpers.api_request import request_url
from helpers.api_token import get_token

token = get_token(settings.CREDENTIALS_ADM)
token_user_squad = get_token(settings.CREDENTIALS_ADM_SQUAD)
token_unprivileges = get_token(settings.CREDENTIALS_USER)
data_user = settings.DEPLOY_VARS_USER
data = settings.DEPLOY_VARS
data_master = settings.DEPLOY_VARS_MASTER
data_update = settings.DEPLOY_VARS_UPDATE
stack_name = settings.STACK_NAME_AWS
uri = settings.DEPLOY_URI


def get_task_id(task_id):
    response = request_url(
        verb="GET",
        uri=f"tasks/id/{task_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    return response


def test_deploy_stack_stormtrooper():
    response = request_url(
        verb="POST",
        uri=f"deploy/{uri}",
        headers={"Authorization": f"Bearer {token_unprivileges}"},
        json=data_user,
    )
    if response.get("status_code") != 409:
        task_id = response.get("json").get("task").get("task_id")
        while get_task_id(task_id).get("json").get("result").get("state") != "SUCCESS":
            time.sleep(3)
        result = response.get("status_code")
        assert result == 202
    assert response.get("status_code")


def test_deploy_stack_darth_vader():
    response = request_url(
        verb="POST",
        uri=f"deploy/{uri}",
        headers={"Authorization": f"Bearer {token_user_squad}"},
        json=data,
    )
    if response.get("status_code") != 409:
        task_id = response.get("json").get("task").get("task_id")
        while get_task_id(task_id).get("json").get("result").get("state") != "SUCCESS":
            time.sleep(3)
        result = response.get("status_code")
        assert result == 202
    assert response.get("status_code")


def test_deploy_stack_yoda():
    response = request_url(
        verb="POST",
        uri=f"deploy/{uri}",
        headers={"Authorization": f"Bearer {token}"},
        json=data_master,
    )
    if response.get("status_code") != 409:
        task_id = response.get("json").get("task").get("task_id")
        while get_task_id(task_id).get("json").get("result").get("state") != "SUCCESS":
            time.sleep(3)
        result = response.get("status_code")
        assert result == 202
    assert response.get("status_code")


def test_get_deploy_by_id():
    response = request_url(
        verb="GET", uri="deploy/?limit=1", headers={"Authorization": f"Bearer {token}"}
    )
    deploy_id = response.get("json")[0].get("id")
    response = request_url(
        verb="GET",
        uri=f"deploy/{deploy_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    result = response.get("status_code")
    assert result == 200


def test_get_deploy_outputs():
    response = request_url(
        verb="GET", uri="deploy/?limit=1", headers={"Authorization": f"Bearer {token}"}
    )
    deploy_id = response.get("json")[0].get("id")
    response = request_url(
        verb="GET",
        uri=f"deploy/output/{deploy_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    result = response.get("status_code")
    assert result == 200


def test_get_all_tasks():
    response = request_url(
        verb="GET",
        uri="tasks/all?limit=100",
        headers={"Authorization": f"Bearer {token}"},
    )
    result = response.get("status_code")
    assert result == 200


def test_update_stack():
    response = request_url(
        verb="GET", uri="deploy/?limit=1", headers={"Authorization": f"Bearer {token}"}
    )
    deploy_id = response.get("json")[0].get("id")
    response = request_url(
        verb="PATCH",
        uri=f"deploy/{deploy_id}",
        headers={"Authorization": f"Bearer {token}"},
        json=data_update,
    )
    task_id = response.get("json").get("task").get("task_id")
    while get_task_id(task_id).get("json").get("result").get("state") != "SUCCESS":
        time.sleep(3)
    result = response.get("status_code")
    assert result == 202


def test_destroy_stack():
    response = request_url(
        verb="GET", uri="deploy/?limit=1", headers={"Authorization": f"Bearer {token}"}
    )
    deploy_id = response.get("json")[0].get("id")
    response = request_url(
        verb="DELETE",
        uri=f"deploy/{deploy_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    task_id = response.get("json").get("task").get("task_id")
    while get_task_id(task_id).get("json").get("result").get("state") != "SUCCESS":
        time.sleep(3)
    result = response.get("status_code")
    assert result == 200
