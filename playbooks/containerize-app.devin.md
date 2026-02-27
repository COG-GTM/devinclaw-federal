# Playbook: Containerize Legacy Application

> **Required Knowledge:** `enterprise-modernizer`, `security-auditor`

## Overview
Create production-ready Docker containers for legacy applications as part of cloud migration. Includes multi-stage Dockerfiles, docker-compose for local development, and Kubernetes manifests for deployment.

## When to Use
- Moving enterprise applications from bare-metal/VM to container orchestration
- Cloud migration to AWS GovCloud, Azure Government, or agency cloud
- Standardizing deployment across the application portfolio

## Instructions

1. **Analyze application runtime**: Language, framework, runtime version, OS dependencies, file system usage, environment variables, ports, health check endpoints.

2. **Create multi-stage Dockerfile**:
   - Stage 1 (builder): Install dependencies, compile/build
   - Stage 2 (runtime): Minimal base image, copy only artifacts
   - Use distroless or hardened base images (Iron Bank for DoD)
   - No root user in runtime stage
   - HEALTHCHECK instruction

3. **Create docker-compose.yml**: Application + database + cache + any dependent services for local development.

4. **Create Kubernetes manifests** (if targeting K8s):
   - Deployment with resource limits, liveness/readiness probes
   - Service for internal networking
   - ConfigMap for non-sensitive config
   - Secrets reference for credentials (external secrets operator)
   - NetworkPolicy for micro-segmentation (Zero Trust)
   - HorizontalPodAutoscaler

5. **Security hardening**:
   - Scan image with Trivy or Grype for CVEs
   - No secrets in image layers
   - Read-only root filesystem where possible
   - Drop all Linux capabilities, add only what's needed
   - STIG Container Security Guide compliance

6. **Test**: Build image, start container, verify health check, run application test suite inside container.

## Specifications
- Base images: Use agency-approved images (Iron Bank, or hardened official images)
- Image size: Minimize — use multi-stage builds and alpine/distroless where possible
- No secrets baked into images — use runtime injection only
- All containers must run as non-root (UID 1000+)

## Advice
- Legacy apps often assume local file system access — containerize with volumes or refactor to use object storage
- JVM apps need explicit memory limits in both Dockerfile and K8s resource limits
- Test with the same container image in dev, staging, and prod — no image divergence


## Self-Verification (Devin 2.2)

Before declaring this playbook complete:

1. **Run all verification gates**: Execute the full self-verify loop — build, test, lint, typecheck, security scan. If the playbook produced code changes, run the test suite and confirm all tests pass.
2. **Auto-fix failures**: If any gate fails, attempt automated repair. Re-run the failing gate. If it fails again after 2 attempts, escalate to human reviewer.
3. **Computer-use E2E** (if applicable): For changes that affect UI or user-facing functionality, use Devin 2.2 computer use to run the application and verify functional correctness.

## Evidence Pack Generation

On completion, produce `evidence-pack.json` in the output directory:

```json
{
  "playbook": "<this playbook name>",
  "session_id": "<Devin session ID>",
  "timestamp": "<ISO 8601>",
  "artifacts": [
    { "filename": "<file>", "sha256": "<hash>", "stage": "<stage>" }
  ],
  "verification": {
    "tests_passed": true,
    "lint_clean": true,
    "security_scan_clean": true,
    "gates_failed_and_auto_fixed": []
  },
  "knowledge_updates": [],
  "escalations": []
}
```

This evidence pack is required for SDLC validation and audit trail compliance (FAR 4.703).
