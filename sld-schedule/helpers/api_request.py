import requests
from config.api import settings

server = settings.SERVER
port = settings.PORT
api = settings.API


def request_url(verb: str, headers: dict = "", uri: str = "", json: dict = ""):
    response = requests.request(
        verb, headers=headers, url=f"{server}:{port}{api}/{uri}", json=json
    )
    result = {"status_code": response.status_code, "json": response.json()}
    return result


def check_status():
    response = request_url(verb="GET")
    return response


if __name__ == "__main__":
    print(check_status())
