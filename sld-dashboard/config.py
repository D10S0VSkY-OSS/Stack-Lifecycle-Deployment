# -*- encoding: utf-8 -*-

import os

from decouple import config


class Config(object):

    basedir = os.path.abspath(os.path.dirname(__file__))

    # Set up the App SECRET_KEY
    SECRET_KEY = config("SECRET_KEY", default="WeakS3cr3T@")

    # This will create a file in <app> FOLDER
    SQLALCHEMY_DATABASE_URI = "{}://{}:{}@{}:{}/{}".format(
        config("DB_ENGINE", default="mysql"),
        config("DB_USERNAME", default="root"),
        config("DB_PASS", default="123"),
        config("DB_HOST", default="db"),
        config("DB_PORT", default=3306),
        config("DB_NAME", default="restapi"),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Connection
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_POOL_TIMEOUT = 20
    SQLALCHEMY_POOL_RECYCLE = 299


class ProductionConfig(Config):
    DEBUG = False

    # Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600
    # Connection
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_POOL_TIMEOUT = 20
    SQLALCHEMY_POOL_RECYCLE = 299

    # PostgreSQL database
    SQLALCHEMY_DATABASE_URI = "{}://{}:{}@{}:{}/{}".format(
        config("DB_ENGINE", default="mysql"),
        config("DB_USERNAME", default="root"),
        config("DB_PASS", default="123"),
        config("DB_HOST", default="db"),
        config("DB_PORT", default=3306),
        config("DB_NAME", default="restapi"),
    )


class DebugConfig(Config):
    DEBUG = True


# Load all possible configurations
config_dict = {"Production": ProductionConfig, "Debug": DebugConfig}
