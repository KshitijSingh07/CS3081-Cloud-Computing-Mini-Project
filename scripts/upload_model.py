"""Upload a trained model directory to the models bucket."""
import argparse, os
from pathlib import Path
import boto3

p=argparse.ArgumentParser()
p.add_argument("--directory", required=True)
p.add_argument("--version", required=True, choices=["v1","v2"])
a=p.parse_args()
s3=boto3.client("s3", endpoint_url=os.environ["S3_ENDPOINT"],
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"))
base=Path(a.directory)
for f in base.rglob("*"):
    if f.is_file():
        key=f"models/{a.version}/{f.relative_to(base).as_posix()}"
        s3.upload_file(str(f), "models", key)
        print(f"uploaded s3://models/{key}")
