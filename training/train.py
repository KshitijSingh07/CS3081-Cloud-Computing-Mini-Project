"""CPU-capable causal-LM fine-tuning on teacher-generated sequences."""
import argparse
import csv
import json
import random
from pathlib import Path
import yaml
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForCausalLM

class CommandDataset(Dataset):
    def __init__(self, records, tokenizer, max_len):
        self.rows = []
        for row in records:
            target = json.loads(row["teacher_raw"])
            prompt = f"Command: {row['text']}\nJSON:"
            answer = json.dumps(target, ensure_ascii=False, separators=(",", ":"))
            full = prompt + " " + answer + tokenizer.eos_token
            enc = tokenizer(full, truncation=True, max_length=max_len, return_tensors="pt")
            labels = enc["input_ids"].clone()
            prompt_len = len(tokenizer(prompt, add_special_tokens=False)["input_ids"])
            labels[:, :min(prompt_len, labels.shape[1])] = -100
            self.rows.append((enc["input_ids"].squeeze(0), enc["attention_mask"].squeeze(0), labels.squeeze(0)))
    def __len__(self): return len(self.rows)
    def __getitem__(self, i): return self.rows[i]

def collate(batch, pad_id):
    width = max(x[0].numel() for x in batch)
    ids, masks, labels = [], [], []
    for x, m, y in batch:
        pad = width - x.numel()
        ids.append(torch.nn.functional.pad(x, (0, pad), value=pad_id))
        masks.append(torch.nn.functional.pad(m, (0, pad), value=0))
        labels.append(torch.nn.functional.pad(y, (0, pad), value=-100))
    return {"input_ids": torch.stack(ids), "attention_mask": torch.stack(masks), "labels": torch.stack(labels)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="training/config.yaml")
    ap.add_argument("--data", default="data/train.jsonl")
    ap.add_argument("--subset", type=int)
    ap.add_argument("--version", default="v1")
    args = ap.parse_args()
    cfg = yaml.safe_load(Path(args.config).read_text())
    seed = int(cfg["seed"])
    random.seed(seed); torch.manual_seed(seed)
    torch.set_num_threads(max(1, min(4, torch.get_num_threads())))
    records = [json.loads(x) for x in Path(args.data).read_text(encoding="utf-8").splitlines() if x.strip()]
    limit = min(int(cfg["max_train_examples"]), 1500)
    if args.subset: limit = min(limit, args.subset)
    records = records[:limit]
    if not records: raise SystemExit("No training records found; run Task 1 first.")
    tokenizer = AutoTokenizer.from_pretrained(cfg["model_name"])
    if tokenizer.pad_token is None: tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(cfg["model_name"])
    model.train()
    ds = CommandDataset(records, tokenizer, int(cfg["max_sequence_length"]))
    loader = DataLoader(ds, batch_size=int(cfg["batch_size"]), shuffle=True,
                        collate_fn=lambda b: collate(b, tokenizer.pad_token_id))
    optimizer = torch.optim.AdamW(model.parameters(), lr=float(cfg["learning_rate"]))
    epochs = int(cfg["epochs"])
    out_dir = Path("models") / args.version
    out_dir.mkdir(parents=True, exist_ok=True)
    loss_file = Path("training") / ("loss.csv" if args.version == "v1" else f"loss_{args.version}.csv")
    loss_file.parent.mkdir(exist_ok=True)
    with loss_file.open("w", newline="") as f:
        writer = csv.writer(f); writer.writerow(["epoch", "mean_loss"])
        for epoch in range(epochs):
            total = 0.0; steps = 0
            optimizer.zero_grad()
            for step, batch in enumerate(loader, 1):
                result = model(**batch)
                loss = result.loss / int(cfg["gradient_accumulation_steps"])
                loss.backward()
                if step % int(cfg["gradient_accumulation_steps"]) == 0 or step == len(loader):
                    optimizer.step(); optimizer.zero_grad()
                total += float(result.loss.detach()); steps += 1
            mean_loss = total / max(steps, 1)
            writer.writerow([epoch + 1, f"{mean_loss:.6f}"]); f.flush()
            print(f"epoch={epoch+1} mean_loss={mean_loss:.6f}")
    model.save_pretrained(out_dir)
    tokenizer.save_pretrained(out_dir)
    print(f"Saved model and tokenizer to {out_dir}")

if __name__ == "__main__":
    main()
