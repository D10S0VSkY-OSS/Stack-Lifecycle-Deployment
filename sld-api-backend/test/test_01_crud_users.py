from config.api import settings
from helpers.api_request import request_url
from helpers.api_token import get_token

token = get_token(settings.CREDENTIALS_ADM)
token_unprivileges = get_token(settings.CREDENTIALS_USER)
user_adm = settings.USER_ADM
user_test = settings.USER_TEST


def test_update_user_init():
    data = settings.USER_PATCH
    list_user = request_url(
        verb="GET",
        uri=f"users/{user_adm}",
        headers={"Authorization": f"Bearer {token}"},
    )
    id = list_user.get("json").get("id")
    response = request_url(
        verb="PATCH",
        uri=f"users/{id}",
        headers={"Authorization": f"Bearer {token}"},
        json=data,
    )
    assert response.get("status_code") == 400


def test_list_users():
    response = request_url(
        verb="GET", uri="users/?limit=1", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.get("status_code") == 200


def test_users_with_bad_passwd():
    response = request_url(
        verb="POST",
        headers={"Content-Type": "application/json"},
        uri="authenticate/access-token-json",
        json=settings.CREDENTIALS_BAD_PASSWD,
    )
    assert response.get("status_code") == 403


def test_create_unprivilege_user():
    data = settings.USER_POST
    response = request_url(
        verb="POST",
        uri="users/",
        headers={"Authorization": f"Bearer {token}"},
        json=data,
    )
    result = response.get("status_code")
    if result != 409:
        assert result == 200


def test_create_unprivilege_user_squad1():
    data = settings.USER_POST_SQUAD1
    response = request_url(
        verb="POST",
        uri="users/",
        headers={"Authorization": f"Bearer {token}"},
        json=data,
    )
    result = response.get("status_code")
    if result != 400:
        assert result == 200


def test_create_unprivilege_user_squad2():
    data = settings.USER_POST_SQUAD2
    response = request_url(
        verb="POST",
        uri="users/",
        headers={"Authorization": f"Bearer {token}"},
        json=data,
    )
    result = response.get("status_code")
    if result != 400:
        assert result == 200


def test_create_privilege_user_squad1():
    data = settings.USER_POST_PRIV
    response = request_url(
        verb="POST",
        uri="users/",
        headers={"Authorization": f"Bearer {token}"},
        json=data,
    )
    result = response.get("status_code")
    if result != 400:
        assert result == 200


def test_create_bot_user():
    data = settings.USER_SCHEDULE
    response = request_url(
        verb="POST",
        uri="users/",
        headers={"Authorization": f"Bearer {token}"},
        json=data,
    )
    result = response.get("status_code")
    if result != 400:
        assert result == 200


def test_create_unprivilege_user_disable():
    data = settings.USER_POST_OFF
    response = request_url(
        verb="POST",
        uri="users/",
        headers={"Authorization": f"Bearer {token}"},
        json=data,
    )
    result = response.get("status_code")
    if result != 400:
        assert result == 200


def test_try_create_user_as_unprivilege_user():
    token_unprivileges = get_token(settings.CREDENTIALS_USER)
    data = settings.USER_POST
    response = request_url(
        verb="POST",
        uri="users/",
        headers={"Authorization": f"Bearer {token_unprivileges}"},
        json=data,
    )
    result = response.get("status_code")
    assert result == 403


def test_try_create_user_as_not_authenticated_user():
    data = settings.USER_POST
    response = request_url(verb="POST", uri="users/", json=data)
    result = response.get("status_code")
    assert result == 401


def test_try_list_users_as_unprivileges_user():
    token_unprivileges = get_token(settings.CREDENTIALS_USER)
    response = request_url(
        verb="GET",
        uri="users/?limit=1",
        headers={"Authorization": f"Bearer {token_unprivileges}"},
    )
    assert response.get("status_code") == 403


def test_try_list_users_as_not_authenticated_user():
    response = request_url(verb="GET", uri="users/?limit=1")
    assert response.get("status_code") == 401


def test_try_delete_user_as_unprivileges_user():
    token_unprivileges = get_token(settings.CREDENTIALS_USER)
    list_user = request_url(
        verb="GET",
        uri=f"users/{user_test}",
        headers={"Authorization": f"Bearer {token_unprivileges}"},
    )
    id = list_user.get("json").get("id")
    response = request_url(
        verb="DELETE",
        uri=f"users/{id}",
        headers={"Authorization": f"Bearer {token_unprivileges}"},
    )
    assert response.get("status_code") == 403


def test_delete_user_test():
    list_user = request_url(
        verb="GET",
        uri=f"users/{user_test}",
        headers={"Authorization": f"Bearer {token}"},
    )
    id = list_user.get("json").get("id")
    response = request_url(
        verb="DELETE", uri=f"users/{id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.get("status_code") == 200
