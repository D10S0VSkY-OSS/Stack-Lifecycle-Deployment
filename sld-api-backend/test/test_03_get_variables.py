from config.api import settings
from helpers.api_request import request_url
from helpers.api_token import get_token

token = get_token(settings.CREDENTIALS_ADM)
token_unprivileges = get_token(settings.CREDENTIALS_USER)
data = settings.STACK_POST_AWS
stack_name = settings.STACK_NAME_AWS


def test_create_stack_for_test_by_name():
    response = request_url(
        verb="POST",
        uri="stacks/",
        headers={"Authorization": f"Bearer {token}"},
        json=data,
    )
    result = response.get("status_code")
    if result != 409:
        assert result == 200


def test_variables_stack_list_by_id():
    response = request_url(
        verb="GET",
        uri=f"stacks/{stack_name}",
        headers={"Authorization": f"Bearer {token}"},
    )
    stack_id = response.get("json").get("id")

    response = request_url(
        verb="GET",
        uri=f"variables/list?stack={stack_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    result = response.get("status_code")
    assert result == 200


def test_variables_stack_list_by_name():
    response = request_url(
        verb="GET",
        uri=f"variables/list?stack={stack_name}",
        headers={"Authorization": f"Bearer {token}"},
    )
    result = response.get("status_code")
    assert result == 200


def test_variables_stack_json_by_id():
    response = request_url(
        verb="GET",
        uri=f"stacks/{stack_name}",
        headers={"Authorization": f"Bearer {token}"},
    )
    stack_id = response.get("json").get("id")

    response = request_url(
        verb="GET",
        uri=f"variables/json?stack={stack_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    result = response.get("status_code")
    assert result == 200


def test_variables_stack_json_by_name():
    response = request_url(
        verb="GET",
        uri=f"variables/json?stack={stack_name}",
        headers={"Authorization": f"Bearer {token}"},
    )
    result = response.get("status_code")
    assert result == 200
