"""Parallel sequence-level teacher labelling worker using Ollama."""
import json
import os
from pathlib import Path
import requests
import boto3

ROOT = Path(__file__).resolve().parents[1]
INPUT = Path(os.getenv("COMMANDS_FILE", ROOT / "data/commands_pool.jsonl"))
OUT_DIR = Path(os.getenv("SHARD_OUTPUT_DIR", ROOT / "results"))
PROMPT = (ROOT / "prompts/teacher_prompt.txt").read_text(encoding="utf-8")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL = os.getenv("TEACHER_MODEL", "phi3.5")
TEMPERATURE = 0
SEED = 42

def ask_teacher(command: str) -> str:
    response = requests.post(
        f"{OLLAMA_URL.rstrip('/')}/api/generate",
        json={
            "model": MODEL,
            "prompt": f"{PROMPT}\n\nCommand: {command}\nJSON:",
            "stream": False,
            "options": {"temperature": TEMPERATURE, "seed": SEED},
        },
        timeout=600,
    )
    response.raise_for_status()
    return response.json()["response"]

def main():
    shard_index = int(os.environ["SHARD_INDEX"])
    shard_count = int(os.environ["SHARD_COUNT"])
    if shard_count < 1 or not 0 <= shard_index < shard_count:
        raise ValueError("Require SHARD_COUNT >= 1 and 0 <= SHARD_INDEX < SHARD_COUNT")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"teacher-shard-{shard_index}.jsonl"
    s3 = None
    if os.getenv("S3_ENDPOINT"):
        s3 = boto3.client(
            "s3", endpoint_url=os.environ["S3_ENDPOINT"],
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
        source_bucket = os.getenv("DATA_BUCKET", "datasets")
        source_key = os.getenv("COMMANDS_KEY", "commands_pool.jsonl")
        if os.getenv("READ_FROM_S3", "0") == "1":
            INPUT.parent.mkdir(parents=True, exist_ok=True)
            s3.download_file(source_bucket, source_key, str(INPUT))
    count = 0
    with INPUT.open(encoding="utf-8") as source, out_path.open("w", encoding="utf-8") as out:
        for line_no, line in enumerate(source):
            if line_no % shard_count != shard_index:
                continue
            record = json.loads(line)
            raw = ask_teacher(record["text"])
            # Store the exact returned string; cleaning is a separate stage.
            result = {"id": record["id"], "text": record["text"], "teacher_raw": raw}
            out.write(json.dumps(result, ensure_ascii=False) + "\n")
            out.flush()
            count += 1
    if s3 and os.getenv("UPLOAD_SHARDS", "0") == "1":
        target_bucket = os.getenv("DATA_BUCKET", "datasets")
        target_key = f"teacher/shard-{shard_index}.jsonl"
        s3.upload_file(str(out_path), target_bucket, target_key)
        print(f"uploaded=s3://{target_bucket}/{target_key}")
    print(f"shard={shard_index} records={count} output={out_path}")

if __name__ == "__main__":
    main()
