# -*- encoding: utf-8 -*-
import requests
from app.helpers.api_request import request_url
from flask import Blueprint

blueprint = Blueprint(
    "home_blueprint",
    __name__,
    url_prefix="",
    template_folder="templates",
    static_folder="static",
)


@blueprint.context_processor
def status_utility():
    def get_status(task_id, token):
        response = request_url(
            verb="GET",
            uri=f"tasks/id/{task_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        content = response["json"]
        try:
            if response.get("json").get("result").get("status") != "SUCCESS":
                return {"result": response.get("json").get("result").get("status")}
            if content.get("result").get("module").get("rc") != 0:
                return {"result": "ERROR"}
            elif isinstance(response.get("json").get("result").get("module"), dict):
                return {"result": "SUCCESS"}
            else:
                return {"result": "ERROR"}
        except Exception as err:
            return {"result": "ERROR"}

    return dict(task_status=get_status)


@blueprint.context_processor
def log_utility():
    def get_output(task_id, token):
        response = request_url(
            verb="GET",
            uri=f"tasks/id/{task_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        content = response["json"]
        # Revisar log
        try:
            if response.get("json").get("result").get("status") == "FAILURE":
                return {"result": content.get("result").get("module").get("stdout")}
            if response["json"].get("result").get("status") != "SUCCESS":
                return {"result": response["json"].get("result")}
            if content.get("result").get("module").get("rc") != 0:
                return {"result": content.get("result").get("module").get("stdout")}
            data = content.get("result").get("module").get("stdout")
            if data is None:
                return {"result": content.get("result").get("status"), "type": "str"}
            if not isinstance(data, list):
                return {"result": content.get("result").get("module").get("stdout")}
            return {"result": content.get("result").get("module").get("stdout")}
        except Exception as err:
            return {"result": response}

    return dict(task_log=get_output)


@blueprint.context_processor
def unlock():
    def put_unlock(task_id, token):
        response = request_url(
            verb="PUT",
            uri=f"deploy/unlock/{task_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        content = response["json"]
        # Revisar log
        return content.get("result")

    return dict(unlock=put_unlock)
