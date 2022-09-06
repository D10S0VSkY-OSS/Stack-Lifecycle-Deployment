from config.api import settings
from helpers.api_request import request_url
from helpers.api_token import get_token

token = get_token(settings.CREDENTIALS_ADM)
token_unprivileges = get_token(settings.CREDENTIALS_USER)
data = settings.AWS_TEST_ACCOUNT
data_pro = settings.AWS_TEST_ACCOUNT_PRO
data_squad2 = settings.AWS_TEST_ACCOUNT_SQUAD2
data_squad2_pro = settings.AWS_TEST_ACCOUNT_SQUAD2_PRO
stack_name = settings.STACK_NAME_AWS


def test_create_aws_account():
    response = request_url(
        verb="POST",
        uri="accounts/aws",
        headers={"Authorization": f"Bearer {token}"},
        json=data,
    )
    result = response.get("status_code")
    if result != 409:
        assert result == 200


def test_create_aws_account_pro_env():
    response = request_url(
        verb="POST",
        uri="accounts/aws",
        headers={"Authorization": f"Bearer {token}"},
        json=data_pro,
    )
    result = response.get("status_code")
    if result != 409:
        assert result == 200


def test_create_aws_account_squad2():
    response = request_url(
        verb="POST",
        uri="accounts/aws",
        headers={"Authorization": f"Bearer {token}"},
        json=data_squad2,
    )
    result = response.get("status_code")
    if result != 409:
        assert result == 200


def test_create_aws_account_squad2_pro():
    response = request_url(
        verb="POST",
        uri="accounts/aws",
        headers={"Authorization": f"Bearer {token}"},
        json=data_squad2_pro,
    )
    result = response.get("status_code")
    if result != 409:
        assert result == 200


def test_get_aws_account():
    response = request_url(
        verb="GET",
        uri="accounts/aws",
        headers={"Authorization": f"Bearer {token}"},
        json=data,
    )
    result = response.get("status_code")
    assert result == 200
