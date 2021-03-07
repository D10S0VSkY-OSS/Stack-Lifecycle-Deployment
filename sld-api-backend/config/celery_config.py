import os
from celery import Celery


celery_app = None
# Rabbit broker config
RABBIT_USER = os.getenv('RABBIT_USER', "admin")
RABBIT_PASSWD = os.getenv('RABBIT_PASSWD', "admin")
RABBIT_SERVER = os.getenv('RABBIT_SERVER', "rabbit")
RABBIT_SERVER_PORT = os.getenv('RABBIT_SERVER_PORT', "5672")
# Redus backend config
REDIS_USER = os.getenv('REDIS_USER', "")
REDIS_PASSWD = os.getenv('REDIS_PASSWD', "")
REDIS_SERVER = os.getenv('REDIS_SERVER', "redis")
REDIS_SERVER_PORT = os.getenv('REDIS_SERVER_PORT', "6379")
REDIS_DB = os.getenv('REDIS_DB', 0)

if not bool(os.getenv('DOCKER')):  # if running example without docker
    celery_app = Celery(
        "worker",
        backend=f"redis://{REDIS_USER}:{REDIS_PASSWD}@{REDIS_SERVER}:{REDIS_SERVER_PORT}/{REDIS_DB}",
        broker = f"amqp://{RABBIT_USER}:{RABBIT_PASSWD}@{RABBIT_SERVER}:{RABBIT_SERVER_PORT}//"
    )
    celery_app.conf.task_routes={
        "app.worker.celery_worker.test_celery": "api-queue"}
else:  # running example with docker
    celery_app = Celery(
        "worker",
        backend = f"redis://{REDIS_SERVER}:{REDIS_SERVER_PORT}/{REDIS_DB}",
        broker=f"amqp://{RABBIT_USER}:{RABBIT_PASSWD}@{RABBIT_SERVER}:{RABBIT_SERVER_PORT}//"
    )
    celery_app.conf.task_routes={
        "app.app.worker.celery_worker.test_celery": "api-queue"}

celery_app.conf.update(task_track_started=True)
