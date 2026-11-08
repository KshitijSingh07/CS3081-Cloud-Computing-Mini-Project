import json
from pathlib import Path
from worker.clean import clean

def test_clean_rejects_bad_and_deduplicates(tmp_path):
    shard = tmp_path / "shard.jsonl"
    rows = [
        {"id":"C0002","text":"weather in paris","teacher_raw":json.dumps({"intent":"weather_query","date":None,"time":None,"place":"paris"})},
        {"id":"C0001","text":"weather in paris","teacher_raw":json.dumps({"intent":"weather_query","date":None,"time":None,"place":"paris"})},
        {"id":"C0003","text":"set alarm","teacher_raw":"not json"},
    ]
    shard.write_text("".join(json.dumps(r)+"\n" for r in rows))
    out, sha, counts = tmp_path/"train.jsonl", tmp_path/"train.sha256", tmp_path/"counts.json"
    result, digest = clean([shard], out, sha, counts)
    saved = [json.loads(x) for x in out.read_text().splitlines()]
    assert len(saved) == 1 and saved[0]["id"] == "C0001"
    assert result["duplicates"] == 1
    assert result["invalid_json"] == 1
    assert len(digest) == 64
