import os
from celery import Celery


celery_app = None
# Rabbit broker config
BROKER_USER = os.getenv('BROKER_USER', "admin")
BROKER_PASSWD = os.getenv('BROKER_PASSWD', "admin")
BROKER_SERVER = os.getenv('BROKER_SERVER', "rabbit")
BROKER_SERVER_PORT = os.getenv('BROKER_SERVER_PORT', "5672")
# Redus backend config
BACKEND_TYPE = os.getenv('BACKEND_TYPE', "redis")
BACKEND_USER = os.getenv('BACKEND_USER', "")
BACKEND_PASSWD = os.getenv('BACKEND_PASSWD', "")
BACKEND_SERVER = os.getenv('BACKEND_SERVER', "redis")
BACKEND_DB = os.getenv('BACKEND_DB', "0")
BROKER_DB = os.getenv('BACKEND_DB', "3")

if not bool(os.getenv('DOCKER')):  # if running example without docker
    celery_app = Celery(
        "worker",
        backend = f"{BACKEND_TYPE}://{BACKEND_USER}:{BACKEND_PASSWD}@{BACKEND_SERVER}/{BACKEND_DB}",
        broker = f"{BACKEND_TYPE}://{BACKEND_USER}:{BACKEND_PASSWD}@{BACKEND_SERVER}/{BROKER_DB}"
    )
    celery_app.conf.task_routes={
        "app.worker.celery_worker.test_celery": "api-queue"}
else:  # running example with docker
    celery_app = Celery(
        "worker",
        backend = f"{BACKEND_TYPE}://{BACKEND_USER}:{BACKEND_PASSWD}@{BACKEND_SERVER}/{BACKEND_DB}",
        broker = f"{BACKEND_TYPE}://{BACKEND_USER}:{BACKEND_PASSWD}@{BACKEND_SERVER}/{BROKER_DB}"
    )
    celery_app.conf.task_routes={
        "app.app.worker.celery_worker.test_celery": "api-queue"}

celery_app.conf.update(task_track_started=True)
celery_app.conf.result_expires = os.getenv('SLD_RESULT_EXPIRE', "259200")
# see : https://docs.celeryproject.org/en/stable/getting-started/backends-and-brokers/redis.html#redis-caveats
celery_app.conf.broker_transport_options = {'visibility_timeout': 43200}