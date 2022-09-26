import json
import logging
from datetime import datetime

import boto3
from botocore.exceptions import ClientError
from configs.bucket_s3 import settings

s3 = boto3.resource(
    "s3",
    region_name=settings.REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)


class Storage(object):
    def __init__(self, path):
        self.path = path

    def check_bucket(self, bucket_name=settings.BUCKET):
        try:
            return s3.Bucket(bucket_name) in s3.buckets.all()
        except Exception as err:
            raise err

    def _activity_log(self, id, action, data, bucket_name=settings.BUCKET):
        now = datetime.now()
        content = f"{action}: {data}\n"
        try:
            logging.info(f"{content}")
            s3.Object(
                bucket_name,
                f"logs/{id}/{now.year}/{now.month}/{now.day}/{now.hour}/{action}_{id}.log",
            ).put(Body=json.dumps(content))
        except Exception as err:
            raise err

    def get(self, id, bucket_name=settings.BUCKET):
        try:
            # Set object as object s3.backet
            bucket = s3.Bucket(bucket_name)
            # Check if object exists
            if bucket.Object(f"{id}.tfstate").get():
                # Read object
                s3_data = s3.Object(bucket_name, f"{id}.tfstate").get()["Body"].read()
                self._activity_log(id, "state_read", {})
                data_json = json.loads(s3_data)
                return data_json
            return None
        except ClientError as err:
            logging.error(err)
            return False
        except Exception as err:
            raise err

    def put(self, id, info, bucket_name=settings.BUCKET):
        try:
            s3.Object(bucket_name, f"{id}.tfstate").put(Body=json.dumps(info))
            self._activity_log(id, "state_write", info)
        except ClientError as err:
            logging.error(err)
            return False

    def lock(self, id, info, bucket_name=settings.BUCKET):
        try:
            lock_object = f"{id}.lock"
            # Set object as object s3.backet
            bucket = s3.Bucket(bucket_name)
            # Check if object exists
            try:
                if bucket.Object(lock_object).get():
                    s3_data = s3.Object(bucket_name, lock_object).get()["Body"].read()
                    return False, json.loads(s3_data)
            except Exception:
                data = json.dumps(info, indent=4, sort_keys=True)
                s3.Object(bucket_name, lock_object).put(Body=json.dumps(data))
                self._activity_log(id, "lock", data)
                return True, {id}
        except ClientError as err:
            logging.error(err)
            return False
        except Exception:
            return False

    def unlock(self, id, info, bucket_name=settings.BUCKET):
        try:
            lock_object = f"{id}.lock"
            # Set object as object s3.backet
            bucket = s3.Bucket(bucket_name)
            # Delete object if exists
            if bucket.Object(lock_object).get():
                s3.Object(bucket_name, lock_object).delete()
                self._activity_log(
                    id, "unlock", json.dumps(info, indent=4, sort_keys=True)
                )
                return True
            return False
        except ClientError as err:
            logging.error(err)
            return False
