import os

from celery import Celery

celery_app = None
# Rabbit broker config
BROKER_USER = os.getenv("BROKER_USER", "")
BROKER_PASSWD = os.getenv("BROKER_PASSWD", "")
BROKER_SERVER = os.getenv("BROKER_SERVER", "redis")  # use rabbit or redis
BROKER_SERVER_PORT = os.getenv(
    "BROKER_SERVER_PORT", "6379"
)  # use por 6379 for redis or 5672 for RabbitMQ
BROKER_TYPE = os.getenv("BROKER_TYPE", "redis")  # use amqp for RabbitMQ or redis
# Redus backend config
BACKEND_TYPE = os.getenv("BACKEND_TYPE", "db+mysql")
BACKEND_USER = os.getenv("BACKEND_USER", "root")
BACKEND_PASSWD = os.getenv("BACKEND_PASSWD", "123")
BACKEND_SERVER = os.getenv("BACKEND_SERVER", "db")
BACKEND_DB = os.getenv("BACKEND_DB", "restapi")

if not bool(os.getenv("DOCKER")):  # if running example without docker
    celery_app = Celery(
        "worker",
        backend=f"{BACKEND_TYPE}://{BACKEND_USER}:{BACKEND_PASSWD}@{BACKEND_SERVER}/{BACKEND_DB}",
        broker=f"{BROKER_TYPE}://{BROKER_USER}:{BROKER_PASSWD}@{BROKER_SERVER}:{BROKER_SERVER_PORT}//",
    )
    celery_app.conf.task_routes = {"app.worker.celery_worker.test_celery": "api-queue"}
else:  # running example with docker
    celery_app = Celery(
        "worker",
        backend=f"{BACKEND_TYPE}://{BACKEND_USER}:{BACKEND_PASSWD}@{BACKEND_SERVER}/{BACKEND_DB}",
        broker=f"{BACKEND_TYPE}://{BROKER_USER}:{BROKER_PASSWD}@{BROKER_SERVER}:{BROKER_SERVER_PORT}//",
    )
    celery_app.conf.task_routes = {
        "app.app.worker.celery_worker.test_celery": "api-queue"
    }

celery_app.conf.update(task_track_started=True)
celery_app.conf.update(result_extended=True)
celery_app.conf.broker_transport_options = {"visibility_timeout": 28800}  # 8 hours.
celery_app.conf.result_expires = os.getenv("SLD_RESULT_EXPIRE", "259200")
celery_app.conf.broker_connection_retry_on_startup = True