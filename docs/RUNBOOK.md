# Operations runbook

## Build and local checks
```bash
pip install -r requirements-dev.txt
python -m pytest -q
python tools/nacl_sim.py network/nacl.json network/packets_sample.jsonl --check
```

## Cluster lifecycle
```bash
k3d cluster create --config cluster/k3d.yaml
kubectl apply -f k8s/00-namespaces.yaml
kubectl apply -f k8s/seaweedfs.yaml
kubectl -n data port-forward svc/seaweedfs 8333:8333
```
Create buckets and upload the course command pool after setting S3 credentials and `S3_ENDPOINT=http://localhost:8333`.

## Deploy the API
Build and import the image into k3d:
```bash
docker build -f service/Dockerfile -t command-parser:v1 .
k3d image import command-parser:v1 -c cs3081-local
```
Set a real Kubernetes Secret locally. Then apply deployment/service/ingress/HPA manifests. Confirm `/readyz` returns 200 before sending parse requests.

## Reliability evidence
- During a Locust run, change Deployment `MODEL_VERSION` and `MODEL_URI` to v2, then `kubectl rollout status deployment/command-parser -n app`.
- Roll back with `kubectl rollout undo deployment/command-parser -n app`.
- Delete one pod during load and capture the replacement pod.
- Delete all pods and measure Pod creation-to-Ready for three runs.
- With two Ready replicas, use response headers `X-Served-By` and `X-Model-Version` to count traffic.

## Teardown
```bash
k3d cluster delete cs3081-local
```

## Parallel teacher Jobs
```bash
docker build -f worker/Dockerfile -t teacher-worker:local .
k3d image import teacher-worker:local -c cs3081-local
kubectl -n pipeline create secret generic object-store-credentials \
  --from-literal=AWS_ACCESS_KEY_ID='<key>' \
  --from-literal=AWS_SECRET_ACCESS_KEY='<secret>'
kubectl apply -f k8s/worker-jobs.yaml
kubectl -n pipeline logs job/teacher-shard-0
kubectl -n pipeline logs job/teacher-shard-1
```
Verify that each input line number is assigned to exactly one shard and that both jobs complete successfully. If `host.docker.internal` does not resolve inside the Pod, configure a reachable host address for the Ollama service.
