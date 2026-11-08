import argparse, json, os
from pathlib import Path
import requests

PROMPT=Path("prompts/teacher_prompt.txt").read_text(encoding="utf-8")
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--validation",default="data/validation.jsonl")
    p.add_argument("--output",default="results/pred_teacher.jsonl")
    a=p.parse_args()
    url=os.getenv("OLLAMA_URL","http://localhost:11434").rstrip("/")
    model=os.getenv("TEACHER_MODEL","phi3.5")
    out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True)
    with Path(a.validation).open(encoding="utf-8") as source, out.open("w",encoding="utf-8") as dest:
        for line in source:
            if not line.strip(): continue
            row=json.loads(line)
            response=requests.post(url+"/api/generate",json={
                "model":model,"prompt":f"{PROMPT}\n\nCommand: {row['text']}\nJSON:",
                "stream":False,"options":{"temperature":0,"seed":42}
            },timeout=600)
            response.raise_for_status()
            raw=response.json()["response"]
            dest.write(json.dumps({"id":row["id"],"prediction":raw},ensure_ascii=False)+"\n")
if __name__=="__main__": main()
