# -*- encoding: utf-8 -*-
import redis
from app import db, login_manager
from app.base import blueprint
from app.base.forms import LoginForm
from app.base.models import User
from app.helpers.api_token import get_token
from app.helpers.security import vault_encrypt
from flask import redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user


@vault_encrypt
def encrypt(secreto):
    try:
        return secreto
    except Exception as err:
        raise err


# Move to config
r = redis.Redis(host="redis", port=6379, db=1, charset="utf-8", decode_responses=True)


@blueprint.route("/")
def route_default():
    return redirect(url_for("base_blueprint.login"))


## Login & Registration


@blueprint.route("/login", methods=["GET", "POST"])
def login():
    login_form = LoginForm(request.form)
    if "login" in request.form:

        # read form data
        username = request.form["username"]
        password = request.form["password"]

        data_credentials: dict = {"username": username, "password": password}

        # Locate user
        db.session.remove()
        db.engine.dispose()
        user = User.get_by_username(username)

        # Check the password
        if user and user.verify_password(password):
            if not current_user.is_active:
                return render_template(
                    "accounts/login.html",
                    msg="Inactive user ¯\_(ツ)_/¯",
                    form=login_form,
                )
            # Get token user
            token = get_token(data_credentials)
            # Store session in redis by user id
            r.set(current_user.id, encrypt(token))

            login_user(user)
            return redirect(url_for("base_blueprint.route_default"))

        # Something (user or pass) is not ok
        return render_template(
            "accounts/login.html", msg="Wrong user or password", form=login_form
        )
    if not current_user.is_authenticated:
        return render_template("accounts/login.html", form=login_form)
    return redirect(url_for("home_blueprint.index"))


# @blueprint.route("/register", methods=["GET", "POST"])
# def register():
#    LoginForm(request.form)
#    create_account_form = CreateAccountForm(request.form)
#    if "register" in request.form:
#
#        username = request.form["username"]
#        email = request.form["email"]
#
#        # Check usename exists
#        user = User.query.filter_by(username=username).first()
#        if user:
#            return render_template(
#                "accounts/register.html",
#                msg="Username already registered",
#                success=False,
#                form=create_account_form,
#            )
#
#        # Check email exists
#        user = User.query.filter_by(email=email).first()
#        if user:
#            return render_template(
#                "accounts/register.html",
#                msg="Email already registered",
#                success=False,
#                form=create_account_form,
#            )
#
#        # else we can create the user
#        user = User(**request.form)
#        db.session.add(user)
#        db.session.commit()
#
#        return render_template(
#            "accounts/register.html",
#            msg='User created please <a href="/login">login</a>',
#            success=True,
#            form=create_account_form,
#        )
#
#    else:
#        return render_template("accounts/register.html", form=create_account_form)
#


@blueprint.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("base_blueprint.login"))


@blueprint.route("/shutdown")
def shutdown():
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()
    return "Server shutting down..."


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
