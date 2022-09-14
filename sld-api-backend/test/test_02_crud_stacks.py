from config.api import settings
from helpers.api_request import request_url
from helpers.api_token import get_token

token = get_token(settings.CREDENTIALS_ADM)
token_unprivileges = get_token(settings.CREDENTIALS_USER)
aws_data = settings.STACK_POST_AWS
azure_data = settings.STACK_POST_AZURE
aws_stack_name = settings.STACK_NAME_AWS
gcp_data = settings.STACK_POST_GCP
gcp_stack_name = settings.STACK_NAME_GCP


def test_create_stack_aws():
    response = request_url(
        verb="POST",
        uri="stacks/",
        headers={"Authorization": f"Bearer {token}"},
        json=aws_data,
    )
    result = response.get("status_code")
    if result != 409:
        assert result == 200


def test_create_stack_gcp():
    response = request_url(
        verb="POST",
        uri="stacks/",
        headers={"Authorization": f"Bearer {token}"},
        json=gcp_data,
    )
    result = response.get("status_code")
    if result != 409:
        assert result == 200


def test_try_create_stack_as_unprivilege_user():
    response = request_url(
        verb="POST",
        uri="stacks/",
        headers={"Authorization": f"Bearer {token_unprivileges}"},
        json=azure_data,
    )
    result = response.get("status_code")
    assert result == 403


def test_try_create_stack_as_not_authenticated_user():
    response = request_url(
        verb="POST",
        uri="stacks/",
        headers={"Authorization": f"Bearer {token_unprivileges}"},
        json=azure_data,
    )
    result = response.get("status_code")
    assert result == 403


def test_list_stack_by_name():
    response = request_url(
        verb="GET",
        uri=f"stacks/{aws_stack_name}",
        headers={"Authorization": f"Bearer {token}"},
    )
    result = response.get("status_code")
    assert result == 200


def test_try_list_stack_by_name_as_unprivilege_user():
    response = request_url(
        verb="GET",
        uri=f"stacks/{aws_stack_name}",
        headers={"Authorization": f"Bearer {token_unprivileges}"},
    )
    result = response.get("status_code")
    assert result == 200


def test_delete_stack_by_name():
    response = request_url(
        verb="DELETE",
        uri=f"stacks/{aws_stack_name}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.get("status_code") == 200


def test_create_stack_for_test_by_id():
    response = request_url(
        verb="POST",
        uri="stacks/",
        headers={"Authorization": f"Bearer {token}"},
        json=aws_data,
    )
    result = response.get("status_code")
    if result != 409:
        assert result == 200


def test_list_stack_by_id():
    response = request_url(
        verb="GET",
        uri=f"stacks/{aws_stack_name}",
        headers={"Authorization": f"Bearer {token}"},
    )
    stack_id = response.get("json").get("id")
    response = request_url(
        verb="GET",
        uri=f"stacks/{stack_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    result = response.get("status_code")
    assert result == 200


def test_delete_stack_by_id():
    response = request_url(
        verb="GET",
        uri=f"stacks/{aws_stack_name}",
        headers={"Authorization": f"Bearer {token}"},
    )
    stack_id = response.get("json").get("id")
    response = request_url(
        verb="DELETE",
        uri=f"stacks/{stack_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.get("status_code") == 200


def test_create_stack_aws_for_poc():
    response = request_url(
        verb="POST",
        uri="stacks/",
        headers={"Authorization": f"Bearer {token}"},
        json=aws_data,
    )
    result = response.get("status_code")
    if result != 409:
        assert result == 200
