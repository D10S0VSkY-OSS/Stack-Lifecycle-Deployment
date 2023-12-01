# -*- encoding: utf-8 -*-
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
from app.home import blueprint
from app.home.forms import (AwsForm, AzureForm, DeployForm, GcpForm, StackForm,
                            UserForm, CustomProviderForm)
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from jinja2 import TemplateNotFound


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


@blueprint.route("/index")
@login_required
def index():
    return render_template(
        "index.html", segment="index", external_api_dns=external_api_dns
    )

# stream SSE
@blueprint.route('/deploy-stream/<deploy_id>')
@login_required
def deploy_stream(deploy_id):
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        # Get defaults vars by deploy
        endpoint = f"deploy/{deploy_id}"
        # Get deploy data vars and set var for render
        response = request_url(
            verb="GET", uri=f"{endpoint}", headers={"Authorization": f"Bearer {token}"}
        )
        deploy = response.get("json")
        return render_template('deploy-stream.html', deploy=deploy)

@blueprint.route('/stream/<task_id>')
@login_required
def stream(task_id):
    def generate():
        pubsub = s.pubsub(ignore_subscribe_messages=False)
        pubsub.subscribe(f'{task_id}')
        for message in pubsub.listen():
            logging.info(message)
            yield f"data: {message['data']}\n\n"
    return Response(generate(), mimetype='text/event-stream')


@blueprint.route('/status/<task_id>')
@login_required
def status(task_id):
    try:
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        response = request_url(
            verb="GET",
            uri=f"tasks/id/{task_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.get("status_code") == 200:
            data = response.get("json").get("result")
            return jsonify(data) 
        else:
            return jsonify({"status": "Error"}), response.status_code
    except TemplateNotFound:
        return render_template("page-404.html"), 404
    except TypeError:
        return redirect(url_for("base_blueprint.logout"))
    except Exception:
        return render_template("page-500.html"), 500


@blueprint.route('/output/<task_id>')
@login_required
def output(task_id):
    try:
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        response = request_url(
            verb="GET",
            uri=f"tasks/id/{task_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.get("status_code") == 200:
            data = response.get("json").get("result").get("module").get("stdout")
            if not isinstance(data, list):
                data = [data] 
            return data
    except Exception as err:
        print(task_id)
        raise err


# Start Deploy
@blueprint.route("/deploys-list", defaults={"limit": 0})
@blueprint.route("/deploys-list/<int:limit>")
@login_required
def list_deploys(limit):
    try:
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        # get stack info
        endpoint = f"stacks/?limit={limit}"
        if limit == 0:
            endpoint = f"stacks/" 
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


@blueprint.route("/deploy/delete/<int:deploy_id>")
@login_required
def delete_deploy(deploy_id):
    try:
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        endpoint = f"deploy/{deploy_id}"
        response = request_url(
            verb="DELETE",
            uri=f"{endpoint}",
            headers={"Authorization": f"Bearer {token}"},
        )
        if response.get("status_code") == 200:
            flash(f"Deleting infra")
        else:
            flash(response.get("json").get("detail"), "error")
        return redirect(
            url_for("home_blueprint.route_template", template="deploys-list")
        )
    except TemplateNotFound:
        return render_template("page-404.html"), 404
    except TypeError:
        return redirect(url_for("base_blueprint.logout"))
    except Exception:
        return render_template("page-500.html"), 500


@blueprint.route("/deploys/destroy/<int:deploy_id>")
@login_required
def destroy_deploy(deploy_id):
    try:
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        endpoint = f"deploy/{deploy_id}"
        response = request_url(
            verb="PUT", uri=f"{endpoint}", headers={"Authorization": f"Bearer {token}"}
        )
        if response.get("status_code") == 202:
            flash(f"Destroying infra")
        else:
            flash(response["json"]["detail"], "error")
        return redirect(
            url_for("home_blueprint.route_template", template="deploys-list")
        )
    except TemplateNotFound:
        return render_template("page-404.html"), 404
    except TypeError:
        return redirect(url_for("base_blueprint.logout"))
    except Exception:
        return render_template("page-500.html"), 500


@blueprint.route("/deploys/unlock/<int:deploy_id>")
@login_required
def unlock_deploy(deploy_id):
    try:
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        endpoint = f"deploy/unlock/{deploy_id}"
        response = request_url(
            verb="PUT", uri=f"{endpoint}", headers={"Authorization": f"Bearer {token}"}
        )
        if response.get("status_code") == 200:
            flash(f"Unlock deploy")
        else:
            flash(response["json"]["detail"], "error")
        return redirect(
            url_for("home_blueprint.route_template", template="deploys-list")
        )
    except TemplateNotFound:
        return render_template("page-404.html"), 404
    except TypeError:
        return redirect(url_for("base_blueprint.logout"))
    except Exception:
        return render_template("page-500.html"), 500


@blueprint.route("/deploys/redeploy/<int:deploy_id>")
@login_required
def relaunch_deploy(deploy_id):
    try:
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        endpoint = f"deploy/{deploy_id}"

        response = request_url(
            verb="GET", uri=f"{endpoint}", headers={"Authorization": f"Bearer {token}"}
        )
        content = response.get("json")
        data = {
            "start_time": content["start_time"],
            "destroy_time": content["destroy_time"],
            "stack_branch": content["stack_branch"],
            "tfvar_file": content["tfvar_file"],
            "project_path": content["project_path"],
            "variables": content["variables"],
        }
        response = request_url(
            verb="PATCH",
            uri=f"{endpoint}",
            headers={"Authorization": f"Bearer {token}"},
            json=data,
        )

        if response.get("status_code") == 202:
            flash(f"Re-Launch Deploy")
        else:
            flash(response["json"]["detail"], "error")
        return redirect(
            url_for("home_blueprint.route_template", template="deploys-list")
        )
    except TemplateNotFound:
        return render_template("page-404.html"), 404
    except TypeError:
        return redirect(url_for("base_blueprint.logout"))
    except Exception:
        return render_template("page-500.html"), 500


@blueprint.route("/edit-deploy", methods=["GET", "POST"], defaults={"deploy_id": None})
@blueprint.route("/edit-deploy/<deploy_id>", methods=["GET", "POST"])
@login_required
def edit_deploy(deploy_id):
    try:
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        form = DeployForm(request.form)
        # Get defaults vars by deploy
        vars_json = request_url(
            verb="GET",
            uri=f"variables/deploy/{deploy_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        endpoint = f"deploy/{deploy_id}"
        # Get deploy data vars and set var for render
        response = request_url(
            verb="GET", uri=f"{endpoint}", headers={"Authorization": f"Bearer {token}"}
        )
        deploy = response.get("json")
        deploy.get("tfvar_file")

        # When user push data with POST verb
        if request.method == "POST":
            # List for exclude in vars
            form_vars = [
                "csrf_token",
                "button",
                "start_time",
                "destroy_time",
                "sld_key",
                "sld_value",
                "branch",
                "tfvar_file",
                "project_path",
            ]
            # Clean exclude data vars
            data_raw = {
                key: value
                for key, value in request.form.items()
                if key not in form_vars
            }
            # Add custom variables from form
            key_list = request.values.getlist("sld_key")
            value_list = request.values.getlist("sld_value")
            data_raw.update(dict(list(zip(key_list, value_list))))
            # Set vars to json
            variables = json.dumps(convert_to_dict(data_raw))
            # Data dend to deploy
            data = {
                "start_time": form.start_time.data,
                "destroy_time": form.destroy_time.data,
                "stack_branch": form.branch.data.replace(" ",""),
                "tfvar_file": form.tfvar_file.data.replace(" ",""),
                "project_path": form.project_path.data.replace(" ",""),
                "variables": ast.literal_eval(variables),
            }
            if not "deploy" in request.form.get("button"):
                endpoint = f"plan/{deploy_id}"
            # Deploy
            response = request_url(
                verb="PATCH",
                uri=f"{endpoint}",
                headers={"Authorization": f"Bearer {token}"},
                json=data,
            )
            if response.get("status_code") == 202:
                flash(f"Updating deploy")
            else:
                flash(response.get("json").get("detail"), "error")
            return redirect(
                url_for("home_blueprint.route_template", template="deploys-list")
            )

        return render_template(
            "deploy-edit.html",
            name="Edit Deploy",
            form=form,
            deploy=deploy,
            data_json=vars_json["json"],
        )
    except TemplateNotFound:
        return render_template("page-404.html"), 404
    except TypeError:
        return redirect(url_for("base_blueprint.logout"))
    except Exception:
        return render_template("page-500.html"), 500


@blueprint.route("/deploy-plan", methods=["GET", "POST"], defaults={"deploy_id": None})
@blueprint.route("/deploy-plan/<deploy_id>", methods=["GET", "POST"])
@login_required
def get_plan(deploy_id):
    try:
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        form = DeployForm(request.form)
        # Get defaults vars by deploy
        vars_json = request_url(
            verb="GET",
            uri=f"variables/deploy/{deploy_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        endpoint = f"deploy/{deploy_id}"
        # Get deploy data vars and set var for render
        response = request_url(
            verb="GET", uri=f"{endpoint}", headers={"Authorization": f"Bearer {token}"}
        )
        deploy = response.get("json")

        # When user push data with POST verb
        if request.method == "POST":
            # List for exclude in vars
            form_vars = [
                "csrf_token",
                "button",
                "start_time",
                "destroy_time",
                "branch",
                "tfvar_file",
                "project_path",
            ]
            # Clean exclude data vars
            data_raw = {
                key: value
                for key, value in request.form.items()
                if key not in form_vars
            }
            variables = json.dumps(convert_to_dict(data_raw))
            # Data dend to deploy
            data = {
                "name": deploy["name"],
                "stack_name": deploy["stack_name"].replace(" ",""),
                "environment": deploy["environment"].replace(" ",""),
                "start_time": form.start_time.data,
                "destroy_time": form.destroy_time.data,
                "stack_branch": form.branch.data.replace(" ",""),
                "tfvar_file": form.tfvar_file.data.replace(" ",""),
                "project_path": form.project_path.data.replace(" ",""),
                "variables": ast.literal_eval(variables),
            }
            # Deploy
            endpoint = "deploy/plan"
            response = request_url(
                verb="POST",
                uri=f"{endpoint}",
                headers={"Authorization": f"Bearer {token}"},
                json=data,
            )
            task_id = response.get("json").get("task")
            if response.get("status_code") == 202:
                while (
                    get_task_id(token, task_id).get("json").get("result").get("state")
                    != "SUCCESS"
                ):
                    time.sleep(3)
                result = (
                    get_task_id(token, task_id)
                    .get("json")
                    .get("result")
                    .get("module")
                    .get("result")[0]
                )
                filter = ["Plan", "up-to-date"]
                result_filter = [i for i in result if i in filter]

                flash(result_filter)
            else:
                flash(response["json"]["detail"])

        return render_template(
            "deploy-edit.html",
            name="Edit Deploy",
            form=form,
            deploy=deploy,
            data_json=vars_json["json"],
        )
    except ValueError:
        return redirect(url_for("base_blueprint.logout"))

@blueprint.route("/plan/redeploy/<int:deploy_id>")
@login_required
def relaunch_plan(deploy_id):
    try:
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        endpoint = f"deploy/{deploy_id}"

        response = request_url(
            verb="GET", uri=f"{endpoint}", headers={"Authorization": f"Bearer {token}"}
        )
        content = response.get("json")
        data = {
            "start_time": content["start_time"],
            "destroy_time": content["destroy_time"],
            "stack_branch": content["stack_branch"],
            "tfvar_file": content["tfvar_file"],
            "project_path": content["project_path"],
            "variables": content["variables"],
        }
        endpoint = f"plan/{deploy_id}"
        response = request_url(
            verb="PATCH",
            uri=f"{endpoint}",
            headers={"Authorization": f"Bearer {token}"},
            json=data,
        )

        if response.get("status_code") == 202:
            flash(f"planning deploy")
        else:
            flash(response["json"]["detail"], "error")
        return redirect(
            url_for("home_blueprint.route_template", template="deploys-list")
        )
    except TemplateNotFound:
        return render_template("page-404.html"), 404
    except TypeError:
        return redirect(url_for("base_blueprint.logout"))
    except Exception:
        return render_template("page-500.html"), 500


@blueprint.route("/clone-deploy", methods=["GET", "POST"], defaults={"deploy_id": None})
@blueprint.route("/clone-deploy/<deploy_id>", methods=["GET", "POST"])
@login_required
def clone_deploy(deploy_id):
    try:
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        form = DeployForm(request.form)
        aws_response = request_url(
            verb="GET",
            uri=f"accounts/aws/",
            headers={"Authorization": f"Bearer {token}"},
        )
        aws_content = aws_response.get("json")
        # Get data from gcp accounts
        gcp_response = request_url(
            verb="GET",
            uri=f"accounts/gcp/",
            headers={"Authorization": f"Bearer {token}"},
        )
        gcp_content = gcp_response.get("json")
        # Get data from azure accounts
        azure_response = request_url(
            verb="GET",
            uri=f"accounts/azure/",
            headers={"Authorization": f"Bearer {token}"},
        )
        azure_content = azure_response.get("json")
        # Get data from custom providers accounts
        custom_response = request_url(
            verb="GET",
            uri=f"accounts/custom_providers/",
            headers={"Authorization": f"Bearer {token}"},
        )
        custom_content = custom_response.get("json")
        # Get defaults vars by deploy
        vars_json = request_url(
            verb="GET",
            uri=f"variables/deploy/{deploy_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        endpoint = f"deploy/{deploy_id}"
        # Get deploy data vars and set var for render
        response = request_url(
            verb="GET", uri=f"{endpoint}", headers={"Authorization": f"Bearer {token}"}
        )
        deploy = response.get("json")
        deploy.get("tfvar_file")

        # When user push data with POST verb
        if request.method == "POST":
            # List for exclude in vars
            form_vars = [
                "csrf_token",
                "button",
                "start_time",
                "destroy_time",
                "sld_key",
                "sld_value",
                "branch",
                "tfvar_file",
                "project_path",
                "deploy_name",
                "squad",
                "environment",
                "deploy_name"
            ]
            # Clean exclude data vars
            data_raw = {
                key: value
                for key, value in request.form.items()
                if key not in form_vars
            }
            # Add custom variables from form
            key_list = request.values.getlist("sld_key")
            value_list = request.values.getlist("sld_value")
            data_raw.update(dict(list(zip(key_list, value_list))))
            # Set vars to json
            variables = json.dumps(convert_to_dict(data_raw))
            # Data dend to deploy
            data = {
                "name": form.deploy_name.data,
                "environment": form.environment.data,
                "squad": form.squad.data,
                "stack_name": deploy["stack_name"],
                "start_time": form.start_time.data,
                "destroy_time": form.destroy_time.data,
                "stack_branch": form.branch.data.replace(" ",""),
                "tfvar_file": form.tfvar_file.data.replace(" ",""),
                "project_path": form.project_path.data.replace(" ",""),
                "variables": ast.literal_eval(variables),
            }
            if not "deploy" in request.form.get("button"):
                endpoint = f"plan/"
            # Deploy
            response = request_url(
                verb="POST",
                uri=f"{endpoint}",
                headers={"Authorization": f"Bearer {token}"},
                json=data,
            )
            if response.get("status_code") == 202:
                flash(f"Updating deploy")
            else:
                flash(response.get("json").get("detail"), "error")
            return redirect(
                url_for("home_blueprint.route_template", template="deploys-list")
            )

        return render_template(
            "deploy-clone.html",
            name="Edit Deploy",
            form=form,
            deploy=deploy,
            aws_content=aws_content,
            gcp_content=gcp_content,
            azure_content=azure_content,
            custom_content=custom_content,
            data_json=vars_json["json"],
        )
    except TemplateNotFound:
        return render_template("page-404.html"), 404
    except TypeError:
        return redirect(url_for("base_blueprint.logout"))
    except Exception:
        return render_template("page-500.html"), 500


@blueprint.route(
    "/edit-schedule", methods=["GET", "POST"], defaults={"deploy_id": None}
)
@blueprint.route("/edit-schedule/<deploy_id>", methods=["GET", "POST"])
@login_required
def edit_schedule(deploy_id):
    try:
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        form = DeployForm(request.form)

        endpoint = f"deploy/{deploy_id}"
        # Get deploy data vars and set var for render
        response = request_url(
            verb="GET", uri=f"{endpoint}", headers={"Authorization": f"Bearer {token}"}
        )
        deploy = response.get("json")

        # When user push data with POST verb
        if request.method == "POST":
            # List for exclude in vars
            data = {
                "start_time": form.start_time.data,
                "destroy_time": form.destroy_time.data,
            }

            endpoint = f"schedule/{deploy_id}"
            # Deploy
            response = request_url(
                verb="PATCH",
                uri=f"{endpoint}",
                headers={"Authorization": f"Bearer {token}"},
                json=data,
            )

            if response.get("status_code") == 202:
                flash(f"Updating schedule")
            else:
                flash(response.get("json").get("detail"), "error")
            return redirect(
                url_for("home_blueprint.route_template", template="deploys-list")
            )

        return render_template(
            "schedule-edit.html",
            name="Edit schedule",
            form=form,
            deploy=deploy,
        )
    except ValueError:
        return redirect(url_for("base_blueprint.logout"))


# stacks create blueprint


@blueprint.route("/stacks-new", methods=["GET", "POST"])
@login_required
def new_stack():
    try:
        form = StackForm(request.form)
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        squad_acces_form = form.squad_access.data
        squad_acces_form_to_list = squad_acces_form.split(",")
        if request.method == "POST":
            new_stack: dict = {
                "stack_name": form.name.data.replace(" ",""),
                "git_repo": form.git.data.replace(" ",""),
                "branch": form.branch.data.replace(" ",""),
                "squad_access": squad_acces_form_to_list,
                "tf_version": form.tf_version.data.replace(" ",""),
                "project_path": form.project_path.data.replace(" ",""),
                "description": form.description.data,
            }
            response = request_url(
                verb="POST",
                uri="stacks/",
                headers={"Authorization": f"Bearer {token}"},
                json=new_stack,
            )
            if response.get("status_code") == 200:
                flash(f"Created stack {form.name.data}")
            else:
                flash(response["json"]["detail"], "error")

        return render_template(
            "/stacks-new.html", title="New Stack", form=form, active="new_Stack"
        )
    except ValueError:
        return redirect(url_for("base_blueprint.logout"))


@blueprint.route("/edit-stack", methods=["GET", "POST"], defaults={"stack_id": None})
@blueprint.route("/edit-stack/<stack_id>", methods=["GET", "POST"])
@login_required
def edit_stack(stack_id):
    try:
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        form = StackForm(request.form)
        endpoint = f"stacks/{stack_id}"
        # Get deploy data vars and set var for render
        response = request_url(
            verb="GET", uri=f"{endpoint}", headers={"Authorization": f"Bearer {token}"}
        )
        stack = response.get("json")

        # When user push data with POST verb
        if request.method == "POST":
            # Data dend to deploy
            squad_acces_form = form.squad_access_edit.data
            squad_acces_form_to_list = squad_acces_form.split(",")
            update_stack = {
                "stack_name": form.name.data.replace(" ",""),
                "git_repo": form.git.data.replace(" ",""),
                "branch": form.branch.data.replace(" ",""),
                "squad_access": squad_acces_form_to_list,
                "tf_version": form.tf_version.data.replace(" ",""),
                "project_path": form.project_path.data.replace(" ",""),
                "description": form.description.data,
            }
            # Deploy
            response = request_url(
                verb="PATCH",
                uri=f"{endpoint}",
                headers={"Authorization": f"Bearer {token}"},
                json=update_stack,
            )
            if response.get("status_code") == 200:
                flash(f"Updating Stack")
            else:
                flash(response.get("json").get("detail"), "error")
            return redirect(
                url_for("home_blueprint.route_template", template="stacks-list")
            )

        return render_template(
            "stack-edit.html", name="Edit Stack", form=form, stack=stack
        )
    except ValueError:
        return redirect(url_for("base_blueprint.logout"))


@blueprint.route("/stack/delete/<stack_name>")
@login_required
def delete_stack(stack_name):
    try:
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        response = request_url(
            verb="DELETE",
            uri=f"stacks/{stack_name}",
            headers={"Authorization": f"Bearer {token}"},
        )
        if response.get("status_code") == 200:
            result = response["json"].get("result")
            flash(f"Stack {result}")
        else:
            flash(response["json"]["detail"], "error")
        return redirect(
            url_for("home_blueprint.route_template", template="stacks-list")
        )
    except ValueError:
        return redirect(url_for("base_blueprint.logout"))


@blueprint.route("/stack/resync/<stack_id>")
@login_required
def resync_stack(stack_id):
    try:
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        endpoint = f"stacks/{stack_id}"
        # Get deploy data vars and set var for render
        response = request_url(
            verb="GET", uri=f"{endpoint}", headers={"Authorization": f"Bearer {token}"}
        )
        if response.get("status_code") == 200:
            response.get("json").get("branch")
            update_stack = {
                "stack_name": response.get("json").get("stack_name"),
                "git_repo": response.get("json").get("git_repo"),
                "branch": response.get("json").get("branch"),
                "squad_access": response.get("json").get("squad_access"),
                "tf_version": response.get("json").get("tf_version"),
                "project_path": response.get("json").get("project_path"),
                "description": response.get("json").get("description"),
            }
            response = request_url(
                verb="PATCH",
                uri=f"{endpoint}",
                headers={"Authorization": f"Bearer {token}"},
                json=update_stack,
            )
            if response.get("status_code") == 200:
                flash(f"Updating Stack")
            else:
                flash(response.get("json").get("detail"), "error")
        else:
            flash(response.get("json").get("detail"), "error")
        return redirect(
            url_for("home_blueprint.route_template", template="stacks-list")
        )
    except ValueError:
        return redirect(url_for("base_blueprint.logout"))


@blueprint.route("/stacks-deploy", methods=["GET", "POST"], defaults={"stack_id": None})
@blueprint.route("/stacks-deploy/<stack_id>", methods=["GET", "POST"])
@login_required
def deploy_stack(stack_id):
    try:
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        form = DeployForm(request.form)
        # Get data from aws accounts
        aws_response = request_url(
            verb="GET",
            uri=f"accounts/aws/",
            headers={"Authorization": f"Bearer {token}"},
        )
        aws_content = aws_response.get("json")
        # Get data from gcp accounts
        gcp_response = request_url(
            verb="GET",
            uri=f"accounts/gcp/",
            headers={"Authorization": f"Bearer {token}"},
        )
        gcp_content = gcp_response.get("json")
        # Get data from azure accounts
        azure_response = request_url(
            verb="GET",
            uri=f"accounts/azure/",
            headers={"Authorization": f"Bearer {token}"},
        )
        azure_content = azure_response.get("json")
        # Get data from custom providers accounts
        custom_response = request_url(
            verb="GET",
            uri=f"accounts/custom_providers/",
            headers={"Authorization": f"Bearer {token}"},
        )
        custom_content = custom_response.get("json")
        # Get data from stack
        stack = request_url(
            verb="GET",
            uri=f"stacks/{stack_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        stack_name = stack["json"]["stack_name"]
        # Get vars from stack
        data_json = request_url(
            verb="GET",
            uri=f"variables/json?stack={stack_name}",
            headers={"Authorization": f"Bearer {token}"},
        )
        vars_json = data_json["json"]
        # Push data vars to api for deploy
        if request.method == "POST":
            # Define list for exclude vars in variables data
            form_vars = [
                "csrf_token",
                "environment",
                "deploy_name",
                "button",
                "start_time",
                "destroy_time",
                "squad",
                "branch",
                "tfvar_file",
                "project_path",
            ]
            variables = {}
            if request.form.get("tfvar_file") == "":
                data_raw = {
                    key: value
                    for key, value in request.form.items()
                    if key not in form_vars
                }
                variables = ast.literal_eval(json.dumps(convert_to_dict(data_raw)))
            data = {
                "name": form.deploy_name.data.replace(" ",""),
                "stack_name": stack["json"]["stack_name"],
                "start_time": form.start_time.data,
                "destroy_time": form.destroy_time.data,
                "squad": request.form.get("squad"),
                "environment": request.form.get("environment"),
                "stack_branch": request.form.get("branch").replace(" ",""),
                "tfvar_file": request.form.get("tfvar_file").replace(" ",""),
                "project_path": request.form.get("project_path").replace(" ",""),
                "variables": variables,
            }
            endpoint = f"plan"
            if not "plan" in request.form.get("button"):
                endpoint = f"deploy"

            # Deploy
            response = request_url(
                verb="POST",
                uri=f"{endpoint}",
                headers={"Authorization": f"Bearer {token}"},
                json=data,
            )
            if response.get("status_code") == 202:
                flash(f"Deploying stack {stack['json']['stack_name']}")
            else:
                flash(response["json"]["detail"], "error")
            return redirect(
                url_for("home_blueprint.route_template", template="deploys-list")
            )
        return render_template(
            "stacks-deploy.html",
            form=form,
            stack=stack,
            sort_form=settings.SORT_BY_DESC,
            aws_content=aws_content,
            gcp_content=gcp_content,
            azure_content=azure_content,
            custom_content=custom_content,
            data_json=vars_json,
        )
    except ValueError:
        return redirect(url_for("base_blueprint.logout"))


# Task
@blueprint.route("/task_id/<task_id>")
@login_required
def get_task(task_id):
    try:
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        response = request_url(
            verb="GET",
            uri=f"tasks/id/{task_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        if response.get("status_code") != 200:
            return render_template("page-500.html"), 500
        try:
            if response["json"]["result"]["status"] != "SUCCESS":
                flash(response["json"]["result"])
            else:
                flash(response["json"]["result"])
        except Exception:
            pass
        return redirect(
            url_for("home_blueprint.route_template", template="deploys-list")
        )
    except ValueError:
        return redirect(url_for("base_blueprint.logout"))


@blueprint.route("/tasks-logs/", defaults={"limit": 0})
@blueprint.route("/tasks-logs/<int:limit>")
@login_required
def list_tasks(limit):
    try:
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        endpoint = f"tasks/all?limit={limit}"
        if limit == 0:
            endpoint = f"tasks/all"
        response = request_url(
            verb="GET", uri=f"{endpoint}", headers={"Authorization": f"Bearer {token}"}
        )
        content = response.get("json")
        return render_template(
            "tasks-logs.html",
            name="Tasks",
            tasks=content,
            external_api_dns=external_api_dns,
        )
    except ValueError:
        return redirect(url_for("base_blueprint.logout"))


@blueprint.route("/task-output", methods=["GET", "POST"], defaults={"task_id": None})
@blueprint.route("/task-output/<task_id>", methods=["GET", "POST"])
@login_required
def list_task(task_id):
    try:
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        endpoint = f"tasks/id/{task_id}"
        response = request_url(
            verb="GET", uri=f"{endpoint}", headers={"Authorization": f"Bearer {token}"}
        )
        content = response.get("json")
        return render_template("tasks-output.html", name="Task", task=content)
    except ValueError:
        return redirect(url_for("base_blueprint.logout"))


# activity logs
@blueprint.route("/activity-logs/", defaults={"limit": 0})
@blueprint.route("/activity-logs/<int:limit>")
@login_required
def list_activity(limit):
    try:
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        endpoint = f"activity/all?limit={limit}"
        if limit == 0:
            endpoint = f"activity/all"
        response = request_url(
            verb="GET", uri=f"{endpoint}", headers={"Authorization": f"Bearer {token}"}
        )
        content = response.get("json")
        return render_template(
            "activity-logs.html",
            name="Activity",
            activity=content,
            external_api_dns=external_api_dns,
        )
    except ValueError:
        return redirect(url_for("base_blueprint.logout"))


# Users


@blueprint.route("/users-new", methods=["GET", "POST"])
@login_required
def new_user():
    try:
        form = UserForm(request.form)
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        if request.method == "POST":
            new_user: dict = {
                "username": form.username.data.replace(" ",""),
                "fullname": form.fullname.data,
                "password": form.password.data,
                "email": form.email.data.replace(" ",""),
                "squad": form.squad.data.split(","),
                "role": request.form.get("role").split(","),
                "is_active": form.is_active.data,
            }
            endpoint = f"users/"
            response = request_url(
                verb="POST",
                uri=f"{endpoint}",
                headers={"Authorization": f"Bearer {token}"},
                json=new_user,
            )
            if response.get("status_code") == 200:
                flash(f"Created user {form.username.data}")
            else:
                flash(response["json"]["detail"], "error")

        return render_template(
            "/users-new.html",
            title="New user",
            form=form,
            active="new_user",
            external_api_dns=external_api_dns,
        )
    except ValueError:
        return redirect(url_for("base_blueprint.logout"))


@blueprint.route("/users-list/", defaults={"limit": 0})
@blueprint.route("/users-list/<int:limit>")
@login_required
def list_users(limit):
    try:
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        endpoint = f"users/?limit={limit}"
        if limit == 0:
            endpoint = f"users/" 
        response = request_url(
            verb="GET", uri=f"{endpoint}", headers={"Authorization": f"Bearer {token}"}
        )
        content = response.get("json")
        return render_template(
            "users-list.html",
            name="Name",
            users=content,
            external_api_dns=external_api_dns,
        )
    except ValueError:
        return redirect(url_for("base_blueprint.logout"))


@blueprint.route("/users/delete/<user_name>")
@login_required
def delete_user(user_name):
    try:
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        endpoint = f"users/{user_name}"
        response = request_url(
            verb="DELETE",
            uri=f"{endpoint}",
            headers={"Authorization": f"Bearer {token}"},
        )
        return redirect(url_for("home_blueprint.route_template", template="users-list"))
    except ValueError:
        return redirect(url_for("base_blueprint.logout"))


@blueprint.route("/users-edit", methods=["GET", "POST"], defaults={"user_id": None})
@blueprint.route("/users-edit/<user_id>", methods=["GET", "POST"])
@login_required
def edit_user(user_id):
    try:
        form = UserForm(request.form)
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        # Get user info by id
        endpoint = f"users/{user_id}"
        response = request_url(
            verb="GET", uri=f"{endpoint}", headers={"Authorization": f"Bearer {token}"}
        )
        vars_json = response["json"]
        vars_json["password"] = "string"
        if request.method == "POST":
            data: dict = {
                "username": request.form.get("username"),
                "fullname": request.form.get("fullname"),
                "password": request.form.get("password"),
                "email": request.form.get("email"),
                "squad": request.form.get("squad").split(","),
                "role": request.form.get("role").split(","),
                "is_active": request.form.get("is_active"),
            }
            # Apply user change
            endpoint = f"users/{user_id}"
            response = request_url(
                verb="PATCH",
                uri=f"{endpoint}",
                headers={"Authorization": f"Bearer {token}"},
                json=data,
            )
            if response.get("status_code") == 200:
                flash(f"User Updated ")
            else:
                flash(response["json"].get("detail"), "error")
            return redirect(
                url_for("home_blueprint.route_template", template="users-list")
            )
        return render_template(
            "users-edit.html", name="Edit User", form=form, data_json=vars_json
        )
    except ValueError:
        return redirect(url_for("base_blueprint.logout"))


@blueprint.route("/user-setting", methods=["GET", "POST"])
@login_required
def setting_user():
    try:
        form = UserForm(request.form)
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        if request.method == "POST":
            user_data: dict = {
                "passwd": form.password.data,
            }
            response = request_url(
                verb="PATCH",
                uri=f"users/reset/",
                headers={"Authorization": f"Bearer {token}"},
                json=user_data,
            )
            if response.get("status_code") == 200:
                flash(f"Password Updated ")
            else:
                flash(response.get("json").get("detail"), "error")
            return redirect(
                url_for("home_blueprint.route_template", template="user-setting")
            )

        return render_template(
            "user-setting.html",
            name="User",
            form=form,
            external_api_dns=external_api_dns,
        )
    except ValueError:
        return redirect(url_for("base_blueprint.logout"))


# Accounts
# AWS


@blueprint.route("/aws-new", methods=["GET", "POST"])
@login_required
def new_aws_account():
    try:
        form = AwsForm(request.form)
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        if request.method == "POST":
            new_user: dict = {
                "squad": form.squad.data.replace(" ",""),
                "environment": form.environment.data.replace(" ",""),
                "access_key_id": form.access_key_id.data.replace(" ",""),
                "secret_access_key": form.secret_access_key.data.replace(" ",""),
                "default_region": form.default_region.data.replace(" ",""),
                "profile_name": form.profile_name.data.replace(" ",""),
                "role_arn": form.role_arn.data.replace(" ",""),
                "source_profile": form.source_profile.data.replace(" ",""),
            }
            response = request_url(
                verb="POST",
                uri="accounts/aws/",
                headers={"Authorization": f"Bearer {token}"},
                json=new_user,
            )
            if response.get("status_code") == 200:
                flash(
                    f"Created aws account for environment {form.environment.data} in {form.squad.data} "
                )
            elif response.get("status_code") == 409:
                flash(response["json"].get("detail"), "error")
            else:
                flash(response["json"], "error")

        return render_template(
            "/aws-new.html",
            title="New aws account",
            form=form,
            active="new_aws_account",
            external_api_dns=external_api_dns,
        )
    except ValueError:
        return redirect(url_for("base_blueprint.logout"))


@blueprint.route("/aws-list")
@login_required
def list_aws_account():
    try:
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        response = request_url(
            verb="GET",
            uri=f"accounts/aws/",
            headers={"Authorization": f"Bearer {token}"},
        )
        content = response.get("json")
        return render_template(
            "aws-list.html", name="Name", aws=content, external_api_dns=external_api_dns
        )

    except ValueError:
        return redirect(url_for("base_blueprint.logout"))


@blueprint.route("/aws/delete/<int:aws_account_id>")
@login_required
def delete_aws_account(aws_account_id):
    try:
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        response = request_url(
            verb="DELETE",
            uri=f"accounts/aws/{aws_account_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        if response.get("status_code") == 200:
            flash(
                f"Account Deleted"
            )
        elif response.get("status_code") == 409:
            flash(response["json"].get("detail"), "error")
        else:
            flash(response["json"], "error")

        return redirect(url_for("home_blueprint.route_template", template="aws-list"))
    except ValueError:
        return redirect(url_for("base_blueprint.logout"))


# gcp
@blueprint.route("/gcp-new", methods=["GET", "POST"])
@login_required
def new_gcp_account():
    try:
        form = GcpForm(request.form)
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        if request.method == "POST":
            new_user: dict = {
                "squad": form.squad.data.replace(" ",""),
                "environment": form.environment.data.replace(" ",""),
                "gcloud_keyfile_json": ast.literal_eval(form.gcloud_keyfile_json.data),
            }
            response = request_url(
                verb="POST",
                uri="accounts/gcp/",
                headers={"Authorization": f"Bearer {token}"},
                json=new_user,
            )
            if response.get("status_code") == 200:
                flash(
                    f"Created gcp account for environment {form.environment.data} in {form.squad.data} "
                )
            elif response.get("status_code") == 409:
                flash(response["json"].get("detail"), "error")
            else:
                flash(response["json"], "error")

        return render_template(
            "/gcp-new.html",
            title="New gcp account",
            form=form,
            active="new_gcp_account",
            external_api_dns=external_api_dns,
        )
    except ValueError:
        return redirect(url_for("base_blueprint.logout"))


@blueprint.route("/gcp-list")
@login_required
def list_gcp_account():
    try:
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        response = request_url(
            verb="GET",
            uri=f"accounts/gcp/",
            headers={"Authorization": f"Bearer {token}"},
        )
        content = response.get("json")
        return render_template(
            "gcp-list.html", name="Name", gcp=content, external_api_dns=external_api_dns
        )
    except ValueError:
        return redirect(url_for("base_blueprint.logout"))


@blueprint.route("/gcp/delete/<int:gcp_account_id>")
@login_required
def delete_gcp_account(gcp_account_id):
    try:
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        response = request_url(
            verb="DELETE",
            uri=f"accounts/gcp/{gcp_account_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        if response.get("status_code") == 200:
            flash(
                f"Account Deleted"
            )
        elif response.get("status_code") == 409:
            flash(response["json"].get("detail"), "error")
        else:
            flash(response["json"], "error")

        return redirect(url_for("home_blueprint.route_template", template="gcp-list"))
    except ValueError:
        return redirect(url_for("base_blueprint.logout"))


# Azure
@blueprint.route("/azure-new", methods=["GET", "POST"])
@login_required
def new_azure_account():
    try:
        form = AzureForm(request.form)
        if request.method == "POST":
            token = decrypt(r.get(current_user.id))
            # Check if token no expired
            check_unauthorized_token(token)
            new_user: dict = {
                "squad": form.squad.data.replace(" ",""),
                "environment": form.environment.data.replace(" ",""),
                "subscription_id": form.subscription_id.data.replace(" ",""),
                "client_id": form.client_id.data.replace(" ",""),
                "client_secret": form.client_secret.data.replace(" ",""),
                "tenant_id": form.tenant_id.data.replace(" ",""),
            }
            response = request_url(
                verb="POST",
                uri="accounts/azure/",
                headers={"Authorization": f"Bearer {token}"},
                json=new_user,
            )
            if response.get("status_code") == 200:
                flash(
                    f"Created azure account for environment {form.environment.data} in {form.squad.data} "
                )
            elif response.get("status_code") == 409:
                flash(response["json"].get("detail"), "error")
            else:
                flash(response["json"], "error")

        return render_template(
            "/azure-new.html",
            title="New azure account",
            form=form,
            active="new_azure_account",
            external_api_dns=external_api_dns,
        )
    except ValueError:
        return redirect(url_for("base_blueprint.logout"))


@blueprint.route("/azure-list")
@login_required
def list_azure_account():
    try:
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        response = request_url(
            verb="GET",
            uri=f"accounts/azure/",
            headers={"Authorization": f"Bearer {token}"},
        )
        content = response.get("json")
        return render_template(
            "azure-list.html",
            name="Name",
            azure=content,
            external_api_dns=external_api_dns,
        )
    except ValueError:
        return redirect(url_for("base_blueprint.logout"))


@blueprint.route("/azure/delete/<int:azure_account_id>")
@login_required
def delete_azure_account(azure_account_id):
    try:
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        response = request_url(
            verb="DELETE",
            uri=f"accounts/azure/{azure_account_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        if response.get("status_code") == 200:
            flash(
                f"Account Deleted"
            )
        elif response.get("status_code") == 409:
            flash(response["json"].get("detail"), "error")
        else:
            flash(response["json"], "error")

        return redirect(url_for("home_blueprint.route_template", template="azure-list"))
    except ValueError:
        return redirect(url_for("base_blueprint.logout"))


# Generic
@blueprint.route("/<template>")
@login_required
def route_template(template):
    try:
        if not template.endswith(".html"):
            template += ".html"
        # Detect the current page
        segment = get_segment(request)
        # Get Token
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        # Get Api data
        deploy_response = request_url(
            verb="GET",
            uri=f"deploy",
            headers={"Authorization": f"Bearer {token}"},
        )
        stack_response = request_url(
            verb="GET",
            uri=f"stacks/",
            headers={"Authorization": f"Bearer {token}"},
        )
        tasks_response = request_url(
            verb="GET",
            uri=f"tasks/all",
            headers={"Authorization": f"Bearer {token}"},
        )
        try:
            api_healthy = request_url(verb="GET", uri=f"")
            schedule_healthy = request_url(
                verb="GET", uri=f"", server=settings.SCHEDULE
            )
            remote_state_healthy = request_url(
                verb="GET", uri=f"", server=settings.REMOTE_STATE
            )
        except Exception as err:
            return err

        stacks = json.loads(stack_response.get("content"))
        deployments = json.loads(deploy_response.get("content"))
        tasks = json.loads(tasks_response.get("content"))

        return render_template(
            template,
            segment=segment,
            user=current_user,
            stacks=stacks,
            deployments=deployments,
            tasks=tasks,
            external_api_dns=external_api_dns,
            api_healthy=api_healthy["json"],
            schedule_healthy=schedule_healthy["json"],
            remote_state_healthy=remote_state_healthy["json"],
        )
    except TemplateNotFound:
        return render_template("page-404.html"), 404
    except ValueError:
        return redirect(url_for("base_blueprint.logout"))
    except Exception:
        return render_template("page-500.html"), 500


# start custom provides
@blueprint.route("/custom-provider-new", methods=["GET", "POST"])
@login_required
def new_custom_providers_account():
    try:
        form = CustomProviderForm(request.form)
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        if request.method == "POST":
            new_provider: dict = {
                "squad": form.squad.data.replace(" ",""),
                "environment": form.environment.data.replace(" ",""),
                "configuration": ast.literal_eval(form.configuration.data),
            }
            response = request_url(
                verb="POST",
                uri="accounts/custom_providers/",
                headers={"Authorization": f"Bearer {token}"},
                json=new_provider,
            )
            if response.get("status_code") == 200:
                flash(
                    f"Created custom provider account for environment {form.environment.data} in {form.squad.data} "
                )
            elif response.get("status_code") == 409:
                flash(response["json"].get("detail"), "error")
            else:
                flash(response["json"], "error")

        return render_template(
            "/custom-provider-new.html",
            title="New custom provider account",
            form=form,
            active="new_custom_providers_account",
            external_api_dns=external_api_dns,
        )
    except ValueError:
        return redirect(url_for("base_blueprint.logout"))


@blueprint.route("/custom-provider-list")
@login_required
def list_custom_providers_account():
    try:
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        response = request_url(
            verb="GET",
            uri=f"accounts/custom_providers/",
            headers={"Authorization": f"Bearer {token}"},
        )
        content = response.get("json")
        return render_template(
            "custom-provider-list.html", name="Name", custom_provider_content=content, external_api_dns=external_api_dns
        )
    except ValueError:
        return redirect(url_for("base_blueprint.logout"))


@blueprint.route("/custom-provider/delete/<int:custom_provider_id>")
@login_required
def delete_custom_providers_account(custom_provider_id):
    try:
        token = decrypt(r.get(current_user.id))
        # Check if token no expired
        check_unauthorized_token(token)
        response = request_url(
            verb="DELETE",
            uri=f"accounts/custom_providers/{custom_provider_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        if response.get("status_code") == 200:
            flash(
                f"Account Deleted"
            )
        elif response.get("status_code") == 409:
            flash(response["json"].get("detail"), "error")
        else:
            flash(response["json"], "error")

        return redirect(url_for("home_blueprint.route_template", template="custom-provider-list"))
    except ValueError:
        return redirect(url_for("base_blueprint.logout"))
# End custom provider

# Helper - Extract current page name from request
def get_segment(request):
    try:
        segment = request.path.split("/")[-1]
        if segment == "":
            segment = "index"
        return segment
    except:
        return None


# Errors


@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template("page-403.html"), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template("page-403.html"), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template("page-404.html"), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template("page-500.html"), 500
