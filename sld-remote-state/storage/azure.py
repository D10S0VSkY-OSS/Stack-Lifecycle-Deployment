# https://docs.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-python?tabs=environment-variable-linux

import json
import logging
from datetime import datetime

from azure.storage.blob import BlobServiceClient
from configs.azure_blob_storage import settings

connect_str = settings.AZURE_STORAGE_CONNECTION_STRING
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_name = settings.CONTAINER
logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)


def check_container(container_name=settings.CONTAINER):
    try:
        return blob_service_client.create_container(container_name)
    except Exception:
        pass


check_container()


class Storage(object):
    def __init__(self, path):
        self.path = path

    def _activity_log(self, id, action, data, container_name=settings.CONTAINER):
        now = datetime.now()
        content = f"{action}: {data}\n"
        try:
            logging.info(f"{content}")
            blob_name = f"logs/{id}/{now.year}/{now.month}/{now.day}/{now.hour}/{action}_{id}.log"
            blob_service_client.get_blob_client(
                container=container_name, blob=blob_name
            )
        except Exception as err:
            raise err

    def get(self, id, container_name=settings.CONTAINER):
        try:
            # Check if object exists
            blob_client = blob_service_client.get_blob_client(
                container=container_name, blob=f"{id}.tfstate"
            )
            if blob_client.exists():
                # Read object
                self._activity_log(id, "state_read", {})
                data_json = json.loads(blob_client.download_blob().readall())
                return data_json
            return None
        except Exception as err:
            logging.error(err)
            return False

    def put(self, id, info, container_name=settings.CONTAINER):
        try:
            blob_client = blob_service_client.get_blob_client(
                container=container_name, blob=f"{id}.tfstate"
            )
            blob_client.upload_blob(json.dumps(info), overwrite=True)
            self._activity_log(id, "state_write", info)
        except Exception as err:
            logging.error(err)
            return False

    def lock(self, id, info, container_name=settings.CONTAINER):
        try:
            # Check if object exists
            blob_client = blob_service_client.get_blob_client(
                container=container_name, blob=f"{id}.lock"
            )
            # Check if object exists
            try:
                if blob_client.exists():
                    data_json = json.loads(blob_client.download_blob().readall())
                    return False, json.loads(data_json)
                data = json.dumps(info, indent=4, sort_keys=True)
                blob_client.upload_blob(data, overwrite=True)
                self._activity_log(id, "lock", data)
                return True, {id}
            except Exception as err:
                logging.error(err)
                return False
        except Exception as err:
            logging.error(err)
            return False

    def unlock(self, id, info, container_name=settings.CONTAINER):
        try:
            # Check if object exists
            blob_client = blob_service_client.get_blob_client(
                container=container_name, blob=f"{id}.lock"
            )
            # Delete object if exists
            if blob_client.exists():
                blob_client.delete_blob()
                self._activity_log(
                    id, "unlock", json.dumps(info, indent=4, sort_keys=True)
                )
                return True
            return False
        except Exception as err:
            logging.error(err)
            return False
