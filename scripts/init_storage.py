"""Create the two required S3 buckets and upload the command pool."""
import os
import boto3
from botocore.exceptions import ClientError

endpoint = os.getenv("S3_ENDPOINT", "http://localhost:8333")
client = boto3.client(
    "s3", endpoint_url=endpoint,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "admin"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "key"),
)
for bucket in ("datasets", "models"):
    try:
        client.create_bucket(Bucket=bucket)
        print("created", bucket)
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code", "")
        if code not in ("BucketAlreadyOwnedByYou", "BucketAlreadyExists"):
            raise
        print("exists", bucket)
client.upload_file("data/commands_pool.jsonl", "datasets", "commands_pool.jsonl")
print("uploaded data/commands_pool.jsonl to s3://datasets/commands_pool.jsonl")
