from azure.storage.blob import BlobServiceClient
from configs.azure_blob_storage import settings

connect_str = settings.AZURE_STORAGE_CONNECTION_STRING
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_name = settings.CONTAINER

try:
    container_client = blob_service_client.create_container(container_name)
except:
    pass


def get(blob_name):
    blob_service_client.get_container_client(container_name)
    blob_list = blob_service_client.list_blobs(blob_name)
    for _blob_data in blob_list:
        json.loads(_blob_data)
