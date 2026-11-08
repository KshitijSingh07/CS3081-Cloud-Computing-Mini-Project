"""Deterministic cleaning of teacher-generated JSONL shards."""
import argparse
import hashlib
import json
from pathlib import Path

INTENTS = {
    "alarm_set", "alarm_query", "calendar_set", "calendar_query",
    "calendar_remove", "weather_query", "datetime_query", "recommendation_events",
}
KEYS = {"intent", "date", "time", "place"}

def clean(shard_paths, output_path, checksum_path, counts_path):
    counts = {
        "input_records": 0,
        "invalid_json": 0,
        "wrong_keys": 0,
        "invalid_intent": 0,
        "slot_not_in_command": 0,
        "duplicates": 0,
        "kept": 0,
    }
    by_id = {}
    for shard in shard_paths:
        with Path(shard).open(encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                counts["input_records"] += 1
                try:
                    rec = json.loads(line)
                    parsed = json.loads(rec["teacher_raw"])
                except (json.JSONDecodeError, KeyError, TypeError):
                    counts["invalid_json"] += 1
                    continue
                if not isinstance(parsed, dict) or set(parsed) != KEYS:
                    counts["wrong_keys"] += 1
                    continue
                if parsed["intent"] not in INTENTS:
                    counts["invalid_intent"] += 1
                    continue
                text = rec.get("text", "")
                if not isinstance(text, str):
                    counts["slot_not_in_command"] += 1
                    continue
                slots = [parsed[k] for k in ("date", "time", "place")]
                if any(v is not None and (not isinstance(v, str) or v not in text) for v in slots):
                    counts["slot_not_in_command"] += 1
                    continue
                rid = str(rec["id"])
                if rid not in by_id:
                    by_id[rid] = {"id": rid, "text": text, "teacher_raw": rec["teacher_raw"]}
    # Duplicate commands: keep the lexicographically smallest ID, as specified.
    sorted_records = sorted(by_id.values(), key=lambda r: r["id"])
    unique = []
    seen = set()
    for rec in sorted_records:
        if rec["text"] in seen:
            counts["duplicates"] += 1
            continue
        seen.add(rec["text"])
        unique.append(rec)
    counts["kept"] = len(unique)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in unique)
    output.write_text(payload, encoding="utf-8")
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    Path(checksum_path).write_text(f"{digest}  {output.name}\n", encoding="utf-8")
    Path(counts_path).write_text(json.dumps(counts, indent=2) + "\n", encoding="utf-8")
    return counts, digest

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("shards", nargs="+")
    parser.add_argument("--output", default="data/train.jsonl")
    parser.add_argument("--checksum", default="data/train.sha256")
    parser.add_argument("--counts", default="results/clean_counts.json")
    args = parser.parse_args()
    counts, digest = clean(args.shards, args.output, args.checksum, args.counts)
    print(json.dumps({"counts": counts, "sha256": digest}, indent=2))

if __name__ == "__main__":
    main()
