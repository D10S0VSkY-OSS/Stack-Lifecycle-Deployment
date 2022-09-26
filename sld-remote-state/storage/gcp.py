# https://cloud.google.com/storage/docs/reference/libraries#create-service-account-console

import json
import logging
from datetime import datetime

from configs.gcp_cloud_storage import settings
from google.cloud import storage

storage_client = storage.Client()
bucket_name = settings.BUCKET
logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)


def check_bucket(bucket_name=settings.BUCKET):
    try:
        return storage_client.create_bucket(bucket_name)
    except Exception:
        pass


check_bucket()


class Storage(object):
    def __init__(self, path):
        self.path = path

    def _activity_log(self, id, action, data, bucket_name=settings.BUCKET):
        now = datetime.now()
        content = f"{action}: {data}\n"
        try:
            logging.info(f"{content}")
            object_name = f"logs/{id}/{now.year}/{now.month}/{now.day}/{now.hour}/{action}_{id}.log"
            bucket = storage_client.get_bucket(bucket_name)
            blob = bucket.blob(object_name)
            blob.upload_from_string(content)
        except Exception as err:
            raise err

    def get(self, id, bucket_name=settings.BUCKET):
        try:
            # Check if object exists
            bucket = storage_client.get_bucket(bucket_name)
            blob = bucket.blob(f"{id}.tfstate")

            if blob.exists():
                # Read object
                self._activity_log(id, "state_read", {})
                data_json = json.loads(blob.download_as_string(client=None))
                return data_json
            return None
        except Exception as err:
            logging.error(err)
            return False

    def put(self, id, info, bucket_name=settings.BUCKET):
        try:
            bucket = storage_client.get_bucket(bucket_name)
            blob = bucket.blob(f"{id}.tfstate")
            data = json.dumps(info, indent=4, sort_keys=True)
            blob.upload_from_string(data)
            self._activity_log(id, "state_write", info)
        except Exception as err:
            logging.error(err)
            return False

    def lock(self, id, info, bucket_name=settings.BUCKET):
        try:
            # Check if object exists
            bucket = storage_client.get_bucket(bucket_name)
            blob = bucket.blob(f"{id}.lock")
            try:
                if blob.exists():
                    data_json = json.loads(blob.download_as_string(client=None))
                    return False, data_json
                data = json.dumps(info, indent=4, sort_keys=True)
                blob.upload_from_string(data)
                self._activity_log(id, "lock", data)
                return True, {id}
            except Exception as err:
                logging.error(err)
                return False
        except Exception as err:
            logging.error(err)
            return False

    def unlock(self, id, info, bucket_name=settings.BUCKET):
        try:
            # Check if object exists
            bucket = storage_client.get_bucket(bucket_name)
            blob = bucket.blob(f"{id}.lock")
            # Delete object if exists
            if blob.exists():
                blob.delete()
                self._activity_log(id, "unlock", info)
                return True
            return False
        except Exception as err:
            logging.error(err)
            return False
