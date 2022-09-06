from .api_request import request_url


def get_token(data):
    response = request_url(
        verb="POST",
        headers={"Content-Type": "application/json"},
        uri="authenticate/access-token-json",
        json=data,
    )
    if response.get("status_code") == 200:
        result = response.get("json")
        return result.get("access_token")
