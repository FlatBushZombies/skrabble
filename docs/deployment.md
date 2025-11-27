---


### `docs/deployment.md`


```md
# Deployment Guide


This is a minimal path to deploy the system to Kubernetes.


## High-level
- Deploy Postgres (managed or in-cluster)
- Deploy Temporal using official Helm chart
- Deploy API, orchestrator worker, and browser worker
- Use PersistentVolumeClaims for artifact storage or S3
- Use HorizontalPodAutoscaler for workers if needed


## Example: Temporal via Helm


```bash
helm repo add temporal https://charts.temporal.io
helm repo update
helm install temporal -n temporal-system temporal/temporal