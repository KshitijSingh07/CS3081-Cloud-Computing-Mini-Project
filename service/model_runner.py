import os
import shutil
from pathlib import Path
from urllib.parse import urlparse
import boto3
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

class ModelRunner:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = "cpu"

    def load(self):
        uri = os.environ["MODEL_URI"]
        endpoint = os.environ["S3_ENDPOINT"]
        parsed = urlparse(uri)
        if parsed.scheme != "s3" or not parsed.netloc:
            raise ValueError("MODEL_URI must look like s3://bucket/prefix/")
        bucket, prefix = parsed.netloc, parsed.path.lstrip("/")
        s3 = boto3.client(
            "s3", endpoint_url=endpoint,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
        local_dir = Path("/tmp/command-parser-model")
        if local_dir.exists():
            shutil.rmtree(local_dir)
        local_dir.mkdir(parents=True)
        found = 0
        paginator = s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            for item in page.get("Contents", []):
                key = item["Key"]
                relative = key[len(prefix):].lstrip("/")
                if not relative:
                    continue
                destination = local_dir / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                s3.download_file(bucket, key, str(destination))
                found += 1
        if found == 0:
            raise RuntimeError(f"No model files found at {uri}")
        self.tokenizer = AutoTokenizer.from_pretrained(local_dir)
        self.model = AutoModelForCausalLM.from_pretrained(local_dir).to(self.device).eval()

    @torch.inference_mode()
    def predict(self, command: str, max_new_tokens: int) -> str:
        if self.model is None:
            raise RuntimeError("model is not loaded")
        prompt = f"Command: {command}\nJSON:"
        inputs = self.tokenizer(prompt, return_tensors="pt")
        output = self.model.generate(
            **inputs, max_new_tokens=max_new_tokens, do_sample=False,
            pad_token_id=self.tokenizer.eos_token_id,
        )
        generated = output[0, inputs["input_ids"].shape[1]:]
        return self.tokenizer.decode(generated, skip_special_tokens=True).strip()
