import datetime

# from dateutil import parser
import requests
from config.api import settings
from fastapi import HTTPException

server = settings.SCHEDULE_SERVER


def resource_life_cycle(start_time: str, end_time: str) -> bool:
    if start_time == 0:
        return None
    date.today().weekday()
    parser_start_time = parser.parse(start_time)
    parser_end_time = parser.parse(end_time)

    now = datetime.datetime.now()
    now_param = datetime.time(now.hour, now.minute, 0)
    start = parser_start_time.time()
    end = parser_end_time.time()

    """Return true if now_param is in the range [start, end]"""
    if start <= end:
        return start <= now_param <= end
    else:
        return start <= now_param or now_param <= end


def request_url(verb: str, headers: dict = "", uri: str = "", json: dict = ""):
    response = requests.request(verb, headers=headers, url=f"{server}/{uri}", json=json)
    try:
        result = {
            "status_code": response.status_code,
            "content": response.content.decode("utf-8"),
            "json": response.json(),
        }
        return result
    except Exception as err:
        raise HTTPException(status_code=501, detail=f"{err}")


def check_status():
    response = request_url(verb="GET")
    return response
