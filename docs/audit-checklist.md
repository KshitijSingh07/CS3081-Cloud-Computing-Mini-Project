# CS3081 project audit

Audit date: 2026-11-08 (Asia/Kolkata)

Status meanings: **Complete and verified** means executed or directly checked; **Implemented but not tested** means code/config exists but cannot be verified in this environment; **Pending** means the requirement is absent or needs work; **Blocked** means an external permission, missing tool, or unavailable resource prevents progress.

## Findings

The repository has files for all seven project tasks. The command pool contains 3,000 records and validation contains 100; IDs and exact command text have zero overlap. Ollama 0.40.15 and `phi3.5:latest` are reachable, and one real inference succeeded. The two-request labeling attempt was stopped at 336 MiB available RAM after preserving 13/3 partial rows under `results/teacher-label-attempt-01-partial/`. The serial attempt's output was preserved before implementing resume. At pause it had 246/1,500 shard-0 rows: 205 valid labels and 41 errors. Wall-clock throughput was 246 rows over 40 min 05 sec, about 6.14 rows/minute. Estimated remaining work was 2,795 inference attempts (unprocessed pool rows plus the 41 errors) or about 7 h 35 min at one request at a time, assuming similar throughput. Resume checks revealed repeated identical prompts after validation errors, so the worker now adds the actual validation feedback on retries. Resume support combines the interrupted checkpoint, prior shard output, and earlier partial attempt, reusing only validated ID/text matches. The run was restarted after resume improvements with one request at a time and a 768 MiB RAM stop threshold; `results/teacher-label-attempt-02/run-resume-monitor.log` records RAM checks. At the latest direct check, the resumed checkpoint had 24 rows (23 valid, 1 error); 2,184 MiB were available. An earlier resumed checkpoint reached 95 rows (77 valid, 18 errors) and recovered one prior failure. The latest restart loaded 205 validated saved labels; repeated identical validation errors now stop after one correction retry. Tests now pass 13 cases. No complete cleaned dataset or training run exists. Python 3.12.6 and development tools are available in `.venv`; Torch/Transformers/FastAPI/Locust are absent. Docker Desktop 4.91.0/Linux Engine 29.8.0 work through approved elevated access; the sandboxed call was denied. A real SeaweedFS 3.80 S3 smoke test passed and its no-volume container was removed. k3d/Helm are absent. Git was initialized with approval; no files are staged or committed.

Task 1 worker supports configurable concurrent requests and per-shard logs. A mocked test covers the full 3,000-row pool as two ordered 1,500-row shards. The live run is still incomplete after the initial memory stop; the safer one-request attempt continues. The cleaner rejects non-string intents and drops all records sharing an ambiguous duplicate ID. SeaweedFS S3 was tested with actual bucket creation/listing, pool upload/download SHA-256 equality, and worker S3 download/upload using the genuine saved C0001 response; the original source hash remained unchanged. No training dataset was written to `data/`.

Current unit tests pass: **13 passed**. Ruff passes for `worker` and `tests`; full requested Ruff scope (`worker tests scripts`) reports **9 style findings in scripts**. The sample NACL simulator passes **6/6** packet cases.

## Requirement checklist

| Requirement | Status | Evidence / next action |
|---|---|---|
| Preserve and use provided command pool | Complete and verified | `data/commands_pool.jsonl` exists; 3,000 lines. |
| Keep validation data out of training | Implemented but not tested | Training defaults to `data/train.jsonl`; the pool/validation ID and exact-text audit found zero overlap, and the worker refuses validation.jsonl; no training run has occurred. |
| Phi-3.5 local Ollama connection | Complete and verified | `/api/tags` returned `phi3.5:latest`; one real training-pool command produced a schema-valid label. |
| Teacher labelling and resume | Implemented; resume run active | At pause: shard 0 had 246/1,500 output rows (205 valid, 41 errors); measured 6.14 rows/minute, estimated 7 h 35 min remaining at concurrency 1. Resume reuses schema-valid exact-ID/text matches across checkpoint and prior outputs, adds validation-error feedback, stops repeated identical validation errors, and refuses accidental overwrite. Restarted with a 768 MiB RAM guard; see `results/teacher-label-attempt-02/run-resume-monitor.log`. Historical log wording caveat is documented in `results/teacher-label-attempt-02/log-interpretation.md`. Tests: 13 passed. |
| Retries, error handling, JSON/schema validation | Complete and verified (mocked faults; live response validation) | Retry recovery/exhaustion, output ordering, error ID/text, real C0001 label validation passed. |
| Invalid/duplicate cleanup and reproducible outputs | Implemented but not tested on full data | 9 tests pass, including malformed intent and ambiguous duplicate-ID handling; no full shard clean/checksum yet. |
| SeaweedFS/S3 upload/download workflow | Complete and verified (local smoke) | `results/s3-integration-check.json` and `.log`: SeaweedFS 3.80 created/listed `datasets` and `models`, uploaded/downloaded 197,541 bytes, and source/download SHA-256 matched (`3470398860500fabcf360debda8fb0e7a8a6ef9f552bc0341b5f3648e335f29a`). `results/s3-worker-integration-check.json` and `.log`: worker S3 read and upload passed for one smoke row, genuine saved C0001 output reused, source hash unchanged, and remote output matched local. Detailed smoke files are under `results/seaweedfs-s3-worker-smoke/`; container was removed without a host volume. |
| Task 1 logs and outputs under `results/` | Pending | Preserved outputs: `results/teacher-label-attempt-01-partial/` and `results/teacher-label-attempt-02/teacher-shard-0.jsonl` (246 rows, 205 valid, 41 errors at pause). Resume code and monitored runner are in `worker/label_worker.py` and `scripts/run_labeling_resume.ps1`; complete shards, final failed-example export, clean counts, train file, and checksum remain pending. |
| Pythia-70M CPU fine-tuning and v1/v2 variation | Implemented but not tested | Trainer/config exist; v2 currently reuses the same config/seed, so genuine variation is pending. |
| Model/version metadata, tokenizer, evaluation | Implemented but not tested | Scripts exist; no model or metrics. |
| FastAPI endpoints, validation, fault handling | Implemented but not tested | Service code and unit tests exist; dependencies/model/Docker engine unavailable. |
| Docker build and image-size verification | Blocked | Engine works; service/worker image build and container tests have not been approved or run. |
| k3d, SeaweedFS, Kubernetes reliability tests | Blocked | Local SeaweedFS container smoke is complete; k3d/Helm absent, no cluster/worker Jobs/API deployment tested. |
| VLSM and NACL behavior | Complete and verified (sample only) | Address plan inspected; simulator sample passed 6/6. Instructor hidden packet set not available. |
| GitHub Actions lint/tests/evaluation/secret scan | Implemented but not tested | 9 local tests pass; full Ruff still fails on 9 script findings; no remote workflow/secret scan. |
| Locust throughput/latency/resource/cost measurements | Pending | Load-test code exists; no server/deployment or results. |
| Final report and handwritten reflection | Pending | Report/reflection template exist; real results and repository URL are missing. |
| ZIP, GitHub Release, final tag | Blocked | Git initialized but no remote URL or final assets; no staging, commit, push, release, or tag. |

## Immediate blockers and constraints

- PyTorch and Transformers are still needed before any training or model evaluation; installation and large model downloads require approval.
- Docker Engine works in the approved elevated shell (`docker version` showed Client and Server); sandbox access to Docker user files is denied. SeaweedFS image is cached, its temporary container has been removed. Ask before creating further containers/images or a k3d cluster.
- The first two-request attempt reached 336 MiB and was stopped. A WMI free-memory query during the serial attempt returned Access denied; the run supervisor stops below 768 MiB. Total RAM and free disk are not verified.
- Git is initialized with approval; no files are staged or committed. Do not commit or push without separate approval.
- External actions (GitHub upload/release and final tag) remain unperformed pending explicit approval, as instructed in the project brief.
