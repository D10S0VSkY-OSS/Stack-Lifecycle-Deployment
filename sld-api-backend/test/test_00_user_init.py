from config.api import settings
from helpers.api_request import request_url


def test_check_status_code_equals_200():
    response = request_url(verb="GET")
    assert response.get("status_code") == 200
    assert response.get("json") == {"status": "healthy"}


def test_create_user_init():
    data = settings.INIT_CREDENTIALS
    response = request_url(verb="POST", uri="users/start", json=data)
    result = response.get("status_code")
    if result != 409:
        assert response.get("status_code") == 200
