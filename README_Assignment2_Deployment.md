# ACEestFitness Assignment 2 – Jenkins + Docker Hub + Kubernetes Strategies

These files are designed to be copied into the existing `samGadhe13/ACEestFitness` repository. The app's container port is **5000** and the health endpoint is **`/health`**.

## Files

- `Jenkinsfile` – CI, tests, Docker image build/push, SonarCloud scan + Quality Gate, and parameter-selected Kubernetes deployments/rollback.
- `sonar-project.properties` – SonarCloud project settings. Replace the two `YOUR_...` values.
- `k8s/rolling.yaml` – Rolling Update; NodePort **30080**.
- `k8s/blue-green.yaml` – Blue/Green; NodePort **30081**; Blue starts as the previous Git tag image and Jenkins switches the service to Green after readiness.
- `k8s/canary.yaml` – Stable (previous version) + 1 current canary replica; NodePort **30082**. Four stable replicas + one canary is an approximate 20% replica ratio, not guaranteed request-level traffic weighting.
- `k8s/ab-test.yaml` – A (previous tagged image) and B (current build) separately exposed on NodePorts **30083** and **30084**. This is separate-version endpoint comparison; no cohort/header-based traffic routing is implemented.
- `k8s/shadow.yaml` – Isolated shadow Deployment/ClusterIP Service (not connected to the production Service). Jenkins smoke-tests it; this is an isolated shadow environment, not production traffic mirroring.

## Before running Jenkins

1. Replace `YOUR_DOCKERHUB_USERNAME` in the Jenkinsfile with your Docker Hub namespace.
2. Replace `YOUR_SONARCLOUD_PROJECT_KEY` and `YOUR_SONARCLOUD_ORGANIZATION_KEY` in both `Jenkinsfile` and `sonar-project.properties` with the exact SonarCloud identifiers.
3. In Jenkins create credentials:
   - Username/password ID `dockerhub-creds` (Docker Hub username and Docker Hub access token as password).
   - Secret Text ID `sonar-token` (SonarCloud analysis token).
4. Jenkins agent must have Docker CLI/daemon access, `kubectl`, and the Minikube user's kubeconfig/context available to the Jenkins service account.
5. Create a Pipeline job using Pipeline script from SCM; repo URL `https://github.com/samGadhe13/ACEestFitness.git`, branch `*/main`, script path `Jenkinsfile`.
6. Ensure Git tag `v1.0.0` is pushed and available to Jenkins. This is the default previous-version tag used by Blue-Green/Canary/A-B.

## Build parameter

`DEPLOY_STRATEGY` choices:

- `NONE`: CI, Docker image push, Sonar scan + gate; no Kubernetes app deployment.
- `ROLLING`: 3 replicas, rolling update with `maxUnavailable: 0` and `maxSurge: 1`.
- `BLUE_GREEN`: builds a baseline image from `BLUE_GIT_TAG` and current image; deploys Blue and Green, waits for both, then switches Service selector to Green.
- `CANARY`: baseline image is Stable (4 replicas), current image is Canary (1 replica), shared Service selects both sets.
- `AB_TEST`: previous-tag image A and current build image B run as separate endpoints.
- `SHADOW`: isolated current-image deployment with a ClusterIP service; no production traffic is redirected or mirrored.
- `ROLLBACK`: runs `kubectl rollout undo` for Rolling if present, switches Blue-Green Service back to Blue if present, and removes the Canary deployment if present.

## NodePort allocation

| Strategy/service | NodePort |
|---|---:|
| Rolling | 30080 |
| Blue-Green | 30081 |
| Canary shared Service | 30082 |
| A/B Version A | 30083 |
| A/B Version B | 30084 |
| Shadow | ClusterIP (no NodePort) |

The NodePorts are distinct and within the Kubernetes default NodePort range. Pods expose container port 5000.

## Run/evidence sequence

Run one Jenkins build per strategy, and save a screenshot of the stage view + console output + workload/service evidence for each. Start with `NONE`, then `ROLLING`, `BLUE_GREEN`, `CANARY`, `AB_TEST`, `SHADOW`, and finally `ROLLBACK` after deployments exist.

The Jenkins pipeline executes application deployment operations. VM terminal commands are reserved for infrastructure/bootstrap and verification (Docker permissions, Minikube, kubectl, Jenkins credentials/job setup).
