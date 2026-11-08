import json
import hashlib
import threading
import time
from pathlib import Path

import pytest
import requests

from worker import label_worker


def test_ask_teacher_retries_transient_request_error(monkeypatch):
    valid = json.dumps({"intent": "datetime_query", "date": None, "time": None, "place": None})

    class Response:
        def raise_for_status(self):
            pass

        def json(self):
            return {"response": valid}

    class Session:
        calls = 0

        def post(self, *args, **kwargs):
            self.calls += 1
            if self.calls == 1:
                raise requests.ConnectionError("simulated transient outage")
            return Response()

    session = Session()
    monkeypatch.setattr(label_worker, "MAX_ATTEMPTS", 3)
    monkeypatch.setattr(label_worker, "RETRY_BASE_SECONDS", 0)

    result = label_worker.ask_teacher("what time is it", session=session)

    assert json.loads(result)["intent"] == "datetime_query"
    assert session.calls == 2


def test_ask_teacher_includes_validation_feedback_on_retry(monkeypatch):
    valid = json.dumps({"intent": "datetime_query", "date": None, "time": None, "place": None})

    class Response:
        def __init__(self, content):
            self.content = content

        def raise_for_status(self):
            pass

        def json(self):
            return {"response": self.content}

    class Session:
        prompts = []

        def post(self, *args, **kwargs):
            self.prompts.append(kwargs["json"]["prompt"])
            return Response("{}" if len(self.prompts) == 1 else valid)

    session = Session()
    monkeypatch.setattr(label_worker, "MAX_ATTEMPTS", 2)
    monkeypatch.setattr(label_worker, "RETRY_BASE_SECONDS", 0)

    assert json.loads(label_worker.ask_teacher("what time is it", session=session))["intent"] == "datetime_query"
    assert len(session.prompts) == 2
    assert "previous response failed validation" in session.prompts[1]
    assert "exactly the required keys" in session.prompts[1]


def test_ask_teacher_stops_repeating_identical_validation_error(monkeypatch):
    class Response:
        def raise_for_status(self):
            pass

        def json(self):
            return {"response": "{}"}

    class Session:
        calls = 0

        def post(self, *args, **kwargs):
            self.calls += 1
            return Response()

    session = Session()
    monkeypatch.setattr(label_worker, "MAX_ATTEMPTS", 4)
    monkeypatch.setattr(label_worker, "RETRY_BASE_SECONDS", 0)

    with pytest.raises(RuntimeError, match=r"after 2 attempts \(limit 4\).+exactly the required keys"):
        label_worker.ask_teacher("what time is it", session=session)
    assert session.calls == 2


def test_two_shards_cover_full_pool_and_write_ordered_logs(tmp_path, monkeypatch):
    root = Path(__file__).resolve().parents[1]
    pool_path = root / "data" / "commands_pool.jsonl"
    source = [json.loads(line) for line in pool_path.read_text(encoding="utf-8").splitlines()]
    monkeypatch.setattr(label_worker, "INPUT", pool_path)
    monkeypatch.setattr(label_worker, "OUT_DIR", tmp_path)
    monkeypatch.setattr(label_worker, "LABEL_WORKERS", 3)

    state = {"active": 0, "peak": 0}
    lock = threading.Lock()

    def fake_teacher(command):
        with lock:
            state["active"] += 1
            state["peak"] = max(state["peak"], state["active"])
        time.sleep(0.001)
        with lock:
            state["active"] -= 1
        return json.dumps(
            {"intent": "datetime_query", "date": None, "time": None, "place": None}
        )

    monkeypatch.setattr(label_worker, "ask_teacher", fake_teacher)
    monkeypatch.setenv("SHARD_COUNT", "2")
    for shard_index in range(2):
        monkeypatch.setenv("SHARD_INDEX", str(shard_index))
        label_worker.main()

    shards = [
        [json.loads(line) for line in (tmp_path / f"teacher-shard-{index}.jsonl").read_text(
            encoding="utf-8"
        ).splitlines()]
        for index in range(2)
    ]
    produced = [record for shard in shards for record in shard]
    assert [len(shard) for shard in shards] == [1500, 1500]
    assert {record["id"] for record in produced} == {record["id"] for record in source}
    assert len(produced) == len({record["id"] for record in produced}) == 3000
    assert all(record["teacher_raw"] for record in produced)
    assert state["peak"] > 1
    for index in range(2):
        log_path = tmp_path / f"teacher-shard-{index}.log"
        assert log_path.exists()
        assert "failures=0" in log_path.read_text(encoding="utf-8")


def test_s3_read_uses_temporary_copy_and_refuses_validation_input(tmp_path, monkeypatch):
    root = Path(__file__).resolve().parents[1]
    pool_path = root / "data" / "commands_pool.jsonl"
    original_hash = hashlib.sha256(pool_path.read_bytes()).hexdigest()
    downloaded_to = []

    class FakeS3:
        def download_file(self, bucket, key, destination):
            downloaded_to.append(Path(destination))
            Path(destination).write_text(
                json.dumps({"id": "SMOKE", "text": "what time is it"}) + "\n",
                encoding="utf-8",
            )

    monkeypatch.setattr(label_worker.boto3, "client", lambda *args, **kwargs: FakeS3())
    monkeypatch.setattr(label_worker, "INPUT", pool_path)
    monkeypatch.setattr(label_worker, "OUT_DIR", tmp_path)
    monkeypatch.setattr(
        label_worker,
        "ask_teacher",
        lambda command: json.dumps(
            {"intent": "datetime_query", "date": None, "time": None, "place": None}
        ),
    )
    monkeypatch.setenv("S3_ENDPOINT", "http://example.invalid")
    monkeypatch.setenv("READ_FROM_S3", "1")
    monkeypatch.setenv("UPLOAD_SHARDS", "0")
    monkeypatch.setenv("SHARD_INDEX", "0")
    monkeypatch.setenv("SHARD_COUNT", "1")

    label_worker.main()

    assert downloaded_to and downloaded_to[0] != pool_path
    assert not downloaded_to[0].exists()
    assert hashlib.sha256(pool_path.read_bytes()).hexdigest() == original_hash
    output = json.loads((tmp_path / "teacher-shard-0.jsonl").read_text(encoding="utf-8"))
    assert output["id"] == "SMOKE"
    with pytest.raises(ValueError, match="validation.jsonl is held out"):
        label_worker.ensure_not_validation(root / "data" / "validation.jsonl")


def test_resume_reuses_valid_labels_and_retries_only_missing_or_failed(tmp_path, monkeypatch):
    source = [
        {"id": "A", "text": "what time is it"},
        {"id": "B", "text": "set an alarm for four pm"},
        {"id": "C", "text": "what is the weather"},
        {"id": "D", "text": "will it rain tomorrow"},
        {"id": "E", "text": "schedule a meeting tomorrow"},
    ]
    input_path = tmp_path / "input.jsonl"
    input_path.write_text("".join(json.dumps(row) + "\n" for row in source), encoding="utf-8")
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    old_output = output_dir / "teacher-shard-0.jsonl"
    valid = json.dumps(
        {"intent": "datetime_query", "date": None, "time": None, "place": None}
    )
    old_output.write_text(
        json.dumps({"id": "A", "text": source[0]["text"], "teacher_raw": valid}) + "\n"
        + json.dumps({"id": "B", "text": source[1]["text"], "error": "old failure"}) + "\n"
        + json.dumps({"id": "C", "text": "wrong source text", "teacher_raw": valid}) + "\n",
        encoding="utf-8",
    )
    with old_output.open("a", encoding="utf-8") as saved:
        saved.write(json.dumps({
            "id": "E",
            "text": source[4]["text"],
            "teacher_raw": json.dumps(
                {"intent": "calendar_set", "date": "tomorrow", "time": None, "place": None}
            ),
        }) + "\n")
    checkpoint = output_dir / "teacher-shard-0.jsonl.resume.jsonl"
    checkpoint.write_text(
        json.dumps({"id": "A", "text": source[0]["text"], "teacher_raw": valid}) + "\n",
        encoding="utf-8",
    )
    prior_attempt = tmp_path / "prior-attempt.jsonl"
    prior_attempt.write_text(
        json.dumps({
            "id": "D",
            "text": source[3]["text"],
            "teacher_raw": json.dumps(
                {"intent": "weather_query", "date": None, "time": None, "place": None}
            ),
        }) + "\n",
        encoding="utf-8",
    )

    calls = []

    def fake_teacher(command):
        calls.append(command)
        intent = "alarm_set" if command.startswith("set an alarm") else "weather_query"
        return json.dumps({"intent": intent, "date": None, "time": None, "place": None})

    monkeypatch.setattr(label_worker, "INPUT", input_path)
    monkeypatch.setattr(label_worker, "OUT_DIR", output_dir)
    monkeypatch.setattr(label_worker, "LABEL_WORKERS", 1)
    monkeypatch.setattr(label_worker, "ask_teacher", fake_teacher)
    monkeypatch.setenv("SHARD_INDEX", "0")
    monkeypatch.setenv("SHARD_COUNT", "1")
    monkeypatch.setenv("RESUME_LABELING", "1")
    monkeypatch.setenv("RESUME_INPUTS", str(prior_attempt))

    label_worker.main()

    output = [json.loads(line) for line in old_output.read_text(encoding="utf-8").splitlines()]
    assert calls == [source[1]["text"], source[2]["text"]]
    assert [row["id"] for row in output] == ["A", "B", "C", "D", "E"]
    assert all("teacher_raw" in row and "error" not in row for row in output)
    assert not (output_dir / "teacher-shard-0.jsonl.resume.jsonl").exists()


def test_worker_refuses_to_overwrite_existing_shard_without_resume(tmp_path, monkeypatch):
    monkeypatch.setattr(label_worker, "OUT_DIR", tmp_path)
    output = tmp_path / "teacher-shard-0.jsonl"
    output.write_text('{"id":"kept"}\n', encoding="utf-8")
    monkeypatch.setenv("SHARD_INDEX", "0")
    monkeypatch.setenv("SHARD_COUNT", "1")
    monkeypatch.delenv("RESUME_LABELING", raising=False)

    with pytest.raises(FileExistsError, match="set RESUME_LABELING=1"):
        label_worker.main()
    assert output.read_text(encoding="utf-8") == '{"id":"kept"}\n'
