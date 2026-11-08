# Attempt 02 log interpretation

The shard log and separate resume stdout/stderr logs are preserved as written.

- The initial attempt (before resume feedback) used up to four Ollama calls per row.
- During the resume run started at 12:23 on 2026-11-08, repeated identical validation errors were stopped early after a correction retry. The error summary still incorrectly printed the configured maximum (`4`) as the actual number of attempts. The warning `validation error repeated after correction; skipping redundant attempts` shows the early stop.
- `worker/label_worker.py` now reports the actual attempt count and the configured limit separately. A regression test verifies the count. Runs started after 12:38 use the corrected message.
- No JSONL labels or source data were changed to alter historical log wording. The current checkpoint and future output rows are generated with the corrected code.
