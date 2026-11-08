"""Generate raw predictions in the instructor score.py input format."""
import argparse
import json
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--validation", default="data/validation.jsonl")
    ap.add_argument("--output", default="results/predictions.jsonl")
    ap.add_argument("--max-new-tokens", type=int, default=96)
    a=ap.parse_args()
    tokenizer=AutoTokenizer.from_pretrained(a.model)
    model=AutoModelForCausalLM.from_pretrained(a.model).to("cpu").eval()
    Path(a.output).parent.mkdir(parents=True,exist_ok=True)
    with Path(a.validation).open(encoding="utf-8") as src, Path(a.output).open("w",encoding="utf-8") as out:
        for line in src:
            if not line.strip(): continue
            row=json.loads(line)
            prompt=f"Command: {row['text']}\nJSON:"
            inputs=tokenizer(prompt,return_tensors="pt")
            with torch.inference_mode():
                tokens=model.generate(**inputs,max_new_tokens=a.max_new_tokens,do_sample=False,
                                      pad_token_id=tokenizer.eos_token_id)
            raw=tokenizer.decode(tokens[0,inputs["input_ids"].shape[1]:],skip_special_tokens=True).strip()
            out.write(json.dumps({"id":row["id"],"prediction":raw},ensure_ascii=False)+"\n")
if __name__=="__main__": main()
