import boto3
from configs.bucket_s3 import settings

s3 = boto3.resource(
    "s3",
    region_name=settings.REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)


def get():
    s3_data = s3.Object(settings.BUCKET, "store/json").get()["Body"].read()
    json.loads(s3_data)
