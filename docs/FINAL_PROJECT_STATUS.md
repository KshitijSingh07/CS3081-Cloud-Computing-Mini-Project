# Final Project Status

## Verified in this package
- Project unit tests: 5 passed (`results/pytest-final.log`).
- NACL simulator: 6/6 expected packet decisions (`results/nacl-final.log`).
- Command pool: 3,000 records and 3,000 unique IDs.
- Validation set: 100 records and 100 unique IDs.
- Pool/validation ID overlap: 0.
- Dataset SHA-256 values: `results/dataset-audit-final.json`.
- Technical report and reflection reference PDFs are present.

## Not complete / not verified
- The reflection PDF is generated handwriting-style artwork, not a verified physical handwritten scan. Replace it with a real scan.
- Teacher labeling of all 3,000 commands and the final cleaned training set.
- Student model training, model/tokenizer files, loss history, and held-out evaluation.
- Docker image build and running API checks.
- Kubernetes cluster deployment, HPA, rollout, rollback, and recovery tests.
- Locust load test and measured latency/throughput/resource results.
- Actual CS3081 GitHub repository, pushed source, CI run, Release assets, and `final` tag.

## Environment limitation for this execution
This build environment has no `docker`, `kubectl`, `k3d`, `helm`, or `ollama` executable. It also has no `data/train.jsonl`, which is required for student training. Therefore those tasks cannot be truthfully completed here.

## Required actions before full compliance
1. Run the teacher labeling pipeline on the machine with Ollama `phi3.5` and complete all shards.
2. Clean the labels and train/evaluate v1 and v2; save model, tokenizer, logs, and checksums.
3. Build and run the Docker API; test health, readiness, parse, and failure behavior.
4. Deploy to k3d/Kubernetes and test rollout, rollback, recovery, and HPA.
5. Run Locust and record actual p50/p95, throughput, failures, and resource measurements.
6. Create/push the actual GitHub project repository, configure CI, publish model/tokenizer/version/checksum as Release assets (never commit model weights), and tag the completed commit `final`.
7. Replace the reflection reference with a physical handwritten scan.
8. Rebuild `230101049.zip`.
