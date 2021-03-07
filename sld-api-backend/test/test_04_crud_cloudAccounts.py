from helpers.api_request import request_url
from helpers.api_token import get_token
from config.api import settings

token = get_token(settings.CREDENTIALS_ADM)
token_unprivileges = get_token(settings.CREDENTIALS_USER)
data = settings.AWS_TEST_ACCOUNT
stack_name = settings.STACK_NAME_AWS


def test_create_aws_account():
    response = request_url(verb='POST', uri='accounts/aws', headers={
                           "Authorization": f"Bearer {token}"}, json=data)
    result = response.get('status_code')
    if result != 400:
        assert result == 200


def test_get_aws_account():
    response = request_url(verb='GET', uri='accounts/aws', headers={
                           "Authorization": f"Bearer {token}"}, json=data)
    result = response.get('status_code')
    assert result == 200
