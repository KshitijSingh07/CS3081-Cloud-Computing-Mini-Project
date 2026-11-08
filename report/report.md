# CS3081 Cloud Computing Mini Project Report

**Student:** Kshitij Singh  
**Roll number:** 230101049  
**Institution:** IIIT Senapati, Manipur  
**Project:** Knowledge Distillation and Deployment of a Lightweight Command-Parsing Language Model on a Local Cloud

## Abstract
This project implements a pipeline for converting natural-language commands into structured JSON using a teacher/student language-model workflow. A Phi-3.5 teacher accessed through Ollama supplies labels; the intended student is EleutherAI/Pythia-70M. The repository includes data validation and cleaning, a labeling worker, a training script, an inference API, container and Kubernetes manifests, an S3-compatible object-storage configuration, network access-control rules, tests, and CI configuration. At the submission snapshot, the object-storage integration and local code-level checks are verified, while full labeling, student training, Kubernetes deployment, and load testing remain incomplete. Results below explicitly distinguish executed checks from planned work.

## 1. Architecture and implementation
The pipeline is organized into five stages: (1) a command pool is split into shards; (2) the Ollama Phi-3.5 teacher is prompted to produce a structured parse; (3) the cleaner validates the schema, intent and slot values and removes invalid or duplicate records; (4) a Pythia-70M student training script consumes the cleaned examples; and (5) a FastAPI service exposes parsing and health/readiness endpoints. Kubernetes manifests describe the API, object storage, worker jobs, ingress and autoscaling. The `network/` directory contains subnet and stateless NACL designs.

The data pool contains **3000 records**, with **3000 unique IDs**. The pool and validation data have **0 overlapping IDs** in the local package audit. The command-pool file is **197,541 bytes**, SHA-256 `3470398860500fabcf360debda8fb0e7a8a6ef9f552bc0341b5f3648e335f29a`.

## 2. Task 1 – Teacher labeling and object storage
The worker uses Ollama with the `phi3.5:latest` model and supports sharded processing, retries, checkpoint/resume, and S3-compatible input/output. A real SeaweedFS 3.80 integration check was reported as successful: two buckets were created; the 197,541-byte command pool was uploaded and downloaded with a matching SHA-256; and the worker S3 download/upload path was exercised using a previously saved genuine C0001 label. The original local dataset hash remained unchanged. The temporary SeaweedFS container was removed after the test.

The full 3,000-record labeling job was not complete at the captured progress snapshot. At **2026-11-08 12:33:40**, shard 0 showed **87/1,500 checkpoint rows**, of which **71 were valid labels and 16 were worker-error rows**. The supervisor reported **2,948 MiB available RAM**. A further **205 previously saved valid labels** were reused by the resume logic; this is a separate prior-output count and must not be added to the 87 checkpoint rows. The run was sequential at that snapshot. These figures are a progress snapshot, not final labeling metrics.

## 3. Task 2 – Student training and evaluation
The repository includes a training configuration for `EleutherAI/pythia-70m`: seed 42, learning rate 0.00005, batch size 1, gradient accumulation 4, 2 epochs, maximum sequence length 192, and a configured maximum of 1,500 training examples. The training script and evaluation utilities are present. **No completed student training run, loss curve, trained model artifact, or measured teacher/student evaluation is included in this submission snapshot.** Consequently, no accuracy, JSON-validity, or full-frame score is claimed.

## 4. Task 3 – Inference API and containerization
The repository contains a FastAPI service, schema validation, model runner, service Dockerfile, and worker Dockerfile. Unit tests pass in the package verification described in Section 7. A successful container image build and a deployed API endpoint were not verified for this report snapshot; Docker Engine access had previously been intermittent. Endpoint performance and memory measurements are therefore not claimed.

## 5. Task 4 – Kubernetes deployment and reliability
Kubernetes manifests are provided for namespaces, SeaweedFS, worker jobs, API Deployment and Service, Ingress, and HPA. The local environment previously lacked k3d and Helm, and a completed Kubernetes deployment, rolling update, rollback, pod-recovery test, or replica distribution measurement is not available. These manifests are implementation artifacts, not evidence of a running cluster.

## 6. Task 5 – Subnetting and NACL
The project includes subnet allocation notes, a simulator-compatible NACL JSON file, and six sample packets. The local simulator command `python tools/nacl_sim.py --check network/nacl.json network/packets_sample.jsonl` returned **6/6 correct (100%)**. The design uses ordered rules and default deny. Since NACLs are stateless, return traffic must be allowed explicitly in the opposite direction; this is documented in `network/nacl-design.md`.

## 7. Task 6 – Reproducibility and CI
A GitHub Actions workflow and dependency/configuration files are included. In the packaged source tree, `python -m pytest -q` returned **0** with output: **[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m                                                                    [100%][0m; [32m[32m[1m5 passed[0m[32m in 0.03s[0m[0m**. The NACL simulator returned **0** and **6/6** expected packet decisions. These are local package checks, not a GitHub Actions run. A GitHub repository URL, successful remote workflow URL, GitHub Release with model/tokenizer assets, and final `final` tag were not supplied or verified.

## 8. Task 7 – Performance and cost
No Locust run, measured request rate, p50/p95 latency, per-pod CPU/memory profile, or cost measurement is included. The repository provides a Locust workload and cost-estimation script, but these are not presented as executed results. A single-laptop/local setup would in any case not demonstrate multi-node fault tolerance.

## 9. Limitations and future work
The main limitation is incomplete execution of the end-to-end pipeline. The teacher labeling process is inference- and memory-intensive; the observed run used sequential processing after an earlier parallel attempt caused memory pressure. Teacher errors require validation-aware retries and explicit failure accounting. Future work is to finish both shards, clean and audit the complete labeled dataset, train the student, evaluate it on the held-out validation set, build and deploy the service, execute reliability and load tests, and publish versioned artifacts. Any future metrics must be generated by those runs and stored under `results/`.

## Appendix A – Reproducibility
See `README.md` for setup and commands, `docs/RUNBOOK.md` for operational steps, `results/submission-evidence.json` for the evidence ledger, and the logs in `results/`. The dataset checksum and local package checks are recorded alongside this report.
