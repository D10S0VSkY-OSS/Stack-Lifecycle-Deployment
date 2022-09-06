import requests

from .config.api import settings

server = settings.SERVER
port = settings.PORT
api = settings.API


def request_url(
    verb: str,
    headers: dict = "",
    uri: str = "",
    json: dict = "",
    server: str = f"{server}:{port}{api}",
):
    try:
        response = requests.request(
            verb, headers=headers, url=f"{server}/{uri}", json=json
        )
        result = {
            "status_code": response.status_code,
            "content": response.content.decode("utf-8"),
            "json": response.json(),
        }
        return result
    except Exception as err:
        result = {
            "status_code": 503,
            "content": f"Service Unavailable {str(err)}",
            "json": f"Service Unavailable {str(err)}",
        }
        return result


def check_unauthorized_token(token):
    response = request_url(
        verb="GET", uri=f"deploy?limit=1", headers={"Authorization": f"Bearer {token}"}
    )
    if response["status_code"] == 401:
        raise ValueError(response["json"]["detail"])


def get_task_id(token, task_id):
    print(token)
    print(task_id)
    response = request_url(
        verb="GET",
        uri=f"tasks/id/{task_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    return response
