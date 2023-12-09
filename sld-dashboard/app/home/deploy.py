# -*- encoding: utf-8 -*-
import os
import ast
import json
import time
import logging
from flask import jsonify, render_template, request, url_for, redirect, flash, Response


import redis
from app import login_manager
from app.helpers.api_request import (check_unauthorized_token, get_task_id,
                                     request_url)
from app.helpers.config.api import settings
from app.helpers.converter import convert_to_dict
from app.helpers.security import vault_decrypt
from flask import Blueprint
from app.home.forms import (AwsForm, AzureForm, DeployForm, GcpForm, StackForm,
                            UserForm, CustomProviderForm)
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from jinja2 import TemplateNotFound


# Icons
def list_icons():
    current_path = os.getcwd()
    base_path = f'{current_path}/app/base/static/assets/img/gallery'
    icons = {}
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.svg'):
                dir_path = os.path.relpath(root, base_path)
                if dir_path not in icons:
                    icons[dir_path] = []
                icons[dir_path].append(file)
    return icons

@vault_decrypt
def decrypt(secreto):
    try:
        return secreto
    except Exception as err:
        raise err


# Move to config file after testing
r = redis.Redis(host="redis", port=6379, db=1, charset="utf-8", decode_responses=True)
s = redis.Redis(host="redis", port=6379, db=15, charset="utf-8", decode_responses=True)

external_api_dns = settings.EXTERNAL_DNS_API


def pretty_json(value):
    return json.dumps(value, indent=4)

deploy_blueprint = Blueprint('deploy_blueprint', __name__)


@deploy_blueprint.route("/deploys-list", defaults={"limit": 0})
@deploy_blueprint.route("/deploys-list/<int:limit>")
@login_required
def list_deploys(limit):
    try:
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        # get stack info
        endpoint = f"stacks/?limit={limit}"
        if limit == 0:
            endpoint = "stacks/" 
        stack_response = request_url(
            verb="GET", uri=f"{endpoint}", headers={"Authorization": f"Bearer {token}"}
        )
        stack = stack_response.get("json")
        # Get deploy data vars and set var for render
        endpoint = f"deploy/?limit={limit}"
        if limit == 0:
            endpoint = f"deploy/" 
        response = request_url(
            verb="GET", uri=f"{endpoint}", headers={"Authorization": f"Bearer {token}"}
        )
        content = response.get("json")
        return render_template(
            "deploys-list.html",
            name="Name",
            token=token,
            deploys=content,
            stacks=stack,
            external_api_dns=external_api_dns,
        )
    except TemplateNotFound:
        return render_template("page-404.html"), 404
    except TypeError:
        return redirect(url_for("base_blueprint.logout"))
    except Exception:
        return render_template("page-500.html"), 500