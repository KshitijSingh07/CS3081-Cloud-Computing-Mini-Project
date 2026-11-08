# Handwritten Reflection – Draft (copy by hand, then scan)

Name: Kshitij Singh
Roll Number: 230101049
Course: CS3081 – Cloud Computing
Project: Knowledge Distillation and Deployment of a Lightweight Command-Parsing Language Model on a Local Cloud

Through this project, I learned how a language-model pipeline can be organized from data preparation and teacher labeling to student training, API serving, object storage, containerization, and Kubernetes deployment. I also learned that a working configuration file or manifest is not the same as a verified deployment; each stage needs execution evidence.

One major challenge was running Phi-3.5 locally for teacher labeling. Parallel requests caused memory pressure, so the labeling workflow was moved to a safer sequential mode with checkpoints and resume support. I also encountered malformed or incomplete teacher outputs. Adding validation-aware retry feedback helped recover at least one previously failing example, while failed rows remained explicitly recorded instead of being treated as valid labels.

I verified the S3-compatible storage workflow against a real SeaweedFS 3.80 container. The command-pool file was uploaded and downloaded with a matching SHA-256 checksum, and the worker's S3 download/upload path was tested using a previously saved genuine label. The original dataset remained unchanged. I also ran the local unit tests and the NACL simulator; the package test suite passed and all six sample packet decisions matched expectations.

The project is not fully complete at this snapshot. Full teacher labeling, student training, Kubernetes deployment, and load testing still need to be completed. I have not claimed unmeasured accuracy or performance numbers. If I continue the project, I will first finish and audit the labels, then train and evaluate the student on a separate validation set, and finally verify deployment and load behavior with saved logs.

The most important lesson was to preserve reproducibility and report limitations honestly. A reliable engineering result should include the commands, configuration, logs, checksums, and test evidence needed for another person to reproduce it.
