---
name: containerization
description: Containerize legacy applications for cloud deployment using Docker, docker-compose, and Kubernetes. Use this skill when packaging enterprise Java/Spring Boot services, legacy .NET Framework applications, or Python workloads into OCI-compliant container images, creating multi-stage Dockerfiles, composing multi-container environments, and generating Kubernetes manifests for deployment to enterprise loud infrastructure.
---

# Application Containerization

## Overview

This skill systematically containerizes legacy applications for cloud-native deployment. It handles the full lifecycle from application profiling and dependency analysis through Dockerfile creation, docker-compose orchestration, Kubernetes manifest generation, and CI/CD pipeline integration. The skill produces production-hardened, minimal-footprint container images that comply with DoD Iron Bank hardening requirements and enterprise security standards.

Enterprises operate hundreds of legacy applications across Java/Spring Boot, .NET Framework, .NET Core, Python, and Node.js stacks. Many of these applications run on dedicated virtual machines or bare-metal servers with snowflake configurations that are difficult to reproduce, scale, or migrate. Containerization is a critical prerequisite for the enterprise's cloud migration strategy, enabling consistent deployments across development, staging, and production environments while reducing infrastructure costs by 30-50% through improved resource utilization and autoscaling.

## What's Needed From User

- **Application source code**: Repository URL or local path to the application to containerize.
- **Runtime requirements**: Language version, framework version, and any native dependencies (e.g., Oracle client libraries, GDAL, ImageMagick).
- **Configuration management**: How the application is currently configured — environment variables, config files, JNDI, Spring profiles, .NET app.config/web.config.
- **External dependencies**: Databases, message queues, caches, file shares, or external services the application connects to.
- **Target platform**: Docker standalone, docker-compose, Kubernetes (EKS, AKS, OpenShift), or a combination.
- **Base image preference** (optional): Iron Bank hardened images preferred; otherwise specify registry (e.g., ECR, Artifactory).
- **Resource requirements** (optional): CPU, memory, and storage estimates for container sizing.
- **Health check endpoints** (optional): Existing health/readiness endpoints, or permission to create them.
- **Secrets management** (optional): Current secrets handling approach and target (Vault, AWS Secrets Manager, K8s Secrets).

## Procedure

1. **Profile application with DeepWiki**
   - Index the application source code, configuration files, build scripts, and deployment artifacts in DeepWiki.
   - Identify the application stack: language, framework, build tool (Maven/Gradle/MSBuild/pip/npm), and runtime version.
   - Map all external dependencies: database connections, API endpoints, message queue bindings, file system paths, and environment variable references.
   - Identify stateful components: file uploads, session storage, local caches, temp directories, and log file paths.
   - Record application startup sequence, initialization dependencies, and graceful shutdown behavior.
   - Identify health check mechanisms or endpoints (Spring Actuator, ASP.NET health checks, custom endpoints).

2. **Assess containerization readiness and plan remediation**
   - Evaluate the application against the Twelve-Factor App methodology:
     - **Codebase**: Single deployable unit per container.
     - **Dependencies**: All dependencies explicitly declared (pom.xml, requirements.txt, package.json, .csproj).
     - **Config**: Configuration externalized to environment variables (not hardcoded).
     - **Backing services**: Database, cache, and queue connections treated as attached resources.
     - **Port binding**: Application self-hosts on a configurable port.
     - **Statelessness**: No local file system state required between requests.
     - **Logs**: Application writes logs to stdout/stderr (not to files).
   - For each violation, create a remediation task:
     - Hardcoded config → Extract to environment variables with sensible defaults.
     - File-based logging → Redirect to stdout/stderr or add a logging framework configuration.
     - Local file storage → Mount a volume or migrate to object storage (S3/MinIO).
     - Fixed port numbers → Make ports configurable via environment variable.
   - Classify remediation effort: Minimal (config changes only), Moderate (code changes for externalization), Significant (architectural changes for statelessness).

3. **Create multi-stage Dockerfile**
   - **Stage 1: Builder**
     - Select the appropriate build image (e.g., `maven:3.9-eclipse-temurin-17` for Java, `mcr.microsoft.com/dotnet/sdk:8.0` for .NET, `python:3.12-slim` for Python).
     - Copy dependency manifests first (pom.xml, package.json, requirements.txt) and install dependencies in a separate layer for cache optimization.
     - Copy source code and build the application.
     - Run unit tests during the build stage to fail fast on broken code.
   - **Stage 2: Runtime**
     - Select the minimal runtime image (e.g., `eclipse-temurin:17-jre-alpine` for Java, `mcr.microsoft.com/dotnet/aspnet:8.0-alpine` for .NET, `python:3.12-alpine` for Python).
     - Prefer Iron Bank hardened base images when available (`registry1.dso.mil/ironbank/`).
     - Copy only the built artifact from Stage 1 (JAR, DLL, wheel, or compiled output).
     - Create a non-root user and switch to it (`USER 1001`).
     - Set `HEALTHCHECK` instruction with appropriate interval, timeout, and retries.
     - Configure the entrypoint with exec form (`ENTRYPOINT ["java", "-jar", "app.jar"]`).
     - Add labels for OCI image spec compliance: `org.opencontainers.image.source`, `org.opencontainers.image.version`, `org.opencontainers.image.created`.
   - Target final image size under 200MB for Java, under 150MB for .NET, under 100MB for Python/Node.js.

4. **Create docker-compose configuration**
   - Define the application service with:
     - Build context pointing to the Dockerfile.
     - Environment variables for all externalized configuration.
     - Port mappings for the application and any debug ports.
     - Volume mounts for persistent data, configuration overlays, and logs.
     - Health check configuration matching the Dockerfile HEALTHCHECK.
     - Restart policy (`unless-stopped` for development, managed by orchestrator in production).
     - Resource limits (CPU and memory) matching production targets.
   - Define backing service containers:
     - PostgreSQL/Oracle with initialization scripts mounted.
     - Redis/Memcached for caching layers.
     - RabbitMQ/Kafka for messaging.
     - MinIO for S3-compatible object storage (development substitute).
   - Define networks for service isolation (frontend, backend, management).
   - Define named volumes for data persistence.
   - Create `.env.example` with all required environment variables documented.
   - Create `docker-compose.override.yml` for development-specific settings (debug ports, hot-reload volumes, relaxed resource limits).

5. **Generate Kubernetes manifests**
   - **Deployment** (`deployment.yaml`):
     - Configure replica count, rolling update strategy (`maxSurge: 1, maxUnavailable: 0`).
     - Set resource requests and limits based on profiling data.
     - Configure liveness probe (restarts unhealthy pods) and readiness probe (removes from service during startup/issues).
     - Set pod disruption budgets for high-availability services.
     - Configure anti-affinity rules to spread pods across nodes/zones.
     - Mount ConfigMaps for configuration and Secrets for credentials.
   - **Service** (`service.yaml`):
     - ClusterIP for internal services, LoadBalancer or NodePort for external-facing services.
     - Configure named ports matching container port declarations.
   - **ConfigMap** (`configmap.yaml`):
     - All non-secret configuration values externalized from the application.
     - Environment-specific overrides via Kustomize overlays or Helm values.
   - **Secret** (`secret.yaml`):
     - Template for secrets (actual values injected by Vault or sealed-secrets in production).
     - Reference external secret stores where possible (ExternalSecrets Operator).
   - **HorizontalPodAutoscaler** (`hpa.yaml`):
     - CPU-based autoscaling with configurable thresholds (default: scale up at 70% CPU).
     - Memory-based autoscaling for memory-intensive workloads.
   - **NetworkPolicy** (`networkpolicy.yaml`):
     - Default deny all ingress; allow only from specified namespaces/pods.
     - Egress rules for database, cache, and external API access.
   - **Ingress** (`ingress.yaml`):
     - TLS termination with cert-manager annotation.
     - Path-based routing for multi-service deployments.
   - Organize manifests using Kustomize with `base/` and `overlays/` (dev, staging, prod) directory structure.

6. **Harden container image**
   - Run Trivy vulnerability scan against the built image; remediate all Critical and High CVEs.
   - Verify no secrets, credentials, or private keys are baked into the image layers (use `docker history` and layer inspection).
   - Ensure the container runs as non-root (UID 1001+).
   - Set filesystem to read-only where possible (`readOnlyRootFilesystem: true` in K8s security context).
   - Drop all Linux capabilities and add back only those required (`drop: ["ALL"]`, `add: ["NET_BIND_SERVICE"]` if needed).
   - Set `seccompProfile: RuntimeDefault` in the pod security context.
   - Verify no package managers (apt, yum, pip) remain in the runtime image.
   - Generate SBOM (Software Bill of Materials) in CycloneDX format for the final image.
   - Validate against Iron Bank hardening guide if targeting DoD environments.

7. **Implement health checks and observability**
   - Create or configure health check endpoints:
     - **Liveness**: `/health/live` — returns 200 if the process is running and not deadlocked.
     - **Readiness**: `/health/ready` — returns 200 only when the application can serve traffic (database connected, caches warm, dependencies available).
     - **Startup**: `/health/startup` — for applications with slow initialization (prevents premature liveness failures).
   - Configure structured logging to stdout in JSON format with correlation IDs.
   - Add Prometheus metrics endpoint (`/metrics`) or OpenTelemetry collector sidecar for observability.
   - Configure distributed tracing with OpenTelemetry SDK if the application participates in service mesh.

8. **Run tests and validate**
   - Build the container image and verify it starts successfully.
   - Execute application test suite inside the container to validate runtime behavior.
   - Run docker-compose up and validate all services start and communicate correctly.
   - Test health check endpoints respond correctly under normal and degraded conditions.
   - Validate environment variable injection and configuration override behavior.
   - Run Trivy scan and confirm zero Critical/High findings.
   - Test graceful shutdown behavior (SIGTERM handling, connection draining).
   - For Kubernetes: deploy to a test cluster and validate pod lifecycle, autoscaling, and network policies.
   - Fix any failures and re-run until all tests pass.

9. **Spawn parallel Devin sessions for fleet containerization**
   - For containerization campaigns with >5 applications, group by technology stack (all Java apps together, all .NET apps together).
   - Spawn parallel Devin sessions (one per application) using the Devin API v3 batch endpoint.
   - Each session receives: the application profile from DeepWiki, remediation plan, base Dockerfile template for the stack, and K8s manifest templates.
   - Monitor all sessions for completion and collect results.
   - Validate cross-application consistency (shared base images, consistent labeling, uniform health check patterns).

10. **Create pull requests and invoke Devin Review**
    - Create one PR per application containing: Dockerfile, docker-compose.yml, K8s manifests, .dockerignore, and any application code changes for containerization readiness.
    - PR description must include: base image used, final image size, Trivy scan summary, health check endpoints, resource limits, and any application code changes required.
    - Invoke Devin Review on each PR for automated quality checks.
    - Address any review findings before merging.

## Specifications

- **OCI compliance**: All container images must comply with the OCI Image Specification v1.0+.
- **Base images**: Prefer Iron Bank hardened images (`registry1.dso.mil/ironbank/`). When unavailable, use official Alpine-based images. Never use `latest` tag — pin to specific version.
- **Image size**: Final runtime images must be under 200MB for Java, 150MB for .NET, 100MB for Python/Node.js. Flag images exceeding these limits for review.
- **Non-root execution**: All containers must run as a non-root user (UID 1001+). No exceptions.
- **Read-only filesystem**: Containers should use `readOnlyRootFilesystem: true` with explicit `emptyDir` mounts for writable paths (temp, logs).
- **No package managers**: Runtime images must not contain package managers (apt, yum, apk, pip, npm). All dependencies installed in builder stage only.
- **Health checks**: Every container must define liveness and readiness probes. Startup probes required for applications with initialization time >30 seconds.
- **Resource limits**: Every Kubernetes deployment must specify CPU and memory requests and limits. Requests must be set based on profiling; limits should be 2x requests as a starting point.
- **Labels**: All images must include OCI-standard labels: `source`, `version`, `created`, `authors`, `description`.
- **Security context**: Kubernetes pods must set `runAsNonRoot: true`, `allowPrivilegeEscalation: false`, `capabilities.drop: ["ALL"]`, and `seccompProfile: RuntimeDefault`.
- **Vulnerability threshold**: Zero Critical or High CVEs in the final image. Medium CVEs must be documented with a mitigation timeline.
- **SBOM**: Every image must have a CycloneDX SBOM generated and stored alongside the image in the registry.
- **Secrets**: No secrets, credentials, API keys, or certificates baked into images. Use Kubernetes Secrets, ExternalSecrets Operator, or Vault Agent Injector.
- **Logging**: Applications must log to stdout/stderr in structured JSON format. No file-based logging inside containers.
- **Batch size**: When using parallel Devin sessions, limit to 10 concurrent sessions per containerization run.

## Advice and Pointers

- Legacy Java applications often depend on JVM flags set in startup scripts. Extract all JVM options (`-Xmx`, `-Xms`, GC flags, system properties) and expose them as environment variables in the Dockerfile's ENTRYPOINT using `JAVA_OPTS` or `JAVA_TOOL_OPTIONS`.
- .NET Framework (not .NET Core) applications cannot run on Linux containers. Use Windows Server Core or Nano Server base images. These are significantly larger (1-2GB) — flag this to the user early and recommend migration to .NET 8 as a precursor to containerization if possible.
- Python applications with C extension dependencies (NumPy, SciPy, GDAL, cryptography) need careful multi-stage builds. Install build tools (gcc, musl-dev) in the builder stage, compile wheels, and copy only the wheels to the runtime stage.
- enterprise applications frequently use Oracle Instant Client for database connectivity. The client libraries are ~200MB and require specific `LD_LIBRARY_PATH` configuration. Use the Oracle-provided container images as builder stage or mount the client as a volume.
- Spring Boot applications should use the layered JAR feature (`java -Djarmode=layertools -jar app.jar extract`) for optimal Docker layer caching — dependencies, Spring, snapshot dependencies, and application layers are separated.
- Always add a `.dockerignore` file before building. Without it, the entire repository (including `.git`, `node_modules`, `target/`, and test data) is sent to the Docker daemon, dramatically slowing builds.
- For Kubernetes, use Kustomize overlays rather than Helm for simple applications. Reserve Helm for applications that need templating across many environments or that will be distributed as packages.
- Container images should be rebuilt weekly even without code changes, to pick up base image security patches. Configure CI/CD accordingly.
- When containerizing applications that write to local disk (logs, temp files, uploads), use `emptyDir` volumes in Kubernetes. For persistent data, use `PersistentVolumeClaim` with the appropriate storage class.
- Test the container with resource limits applied from the start. Many Java applications with `-Xmx` set higher than the container memory limit will be OOM-killed by the kernel with no useful error message.


## Self-Verification Loop (Devin 2.2)

After completing the primary procedure:

1. **Self-verify**: Run all applicable verification gates:
   - Build/test gates: Docker image builds successfully, container starts and passes health checks
   - Security gates: Trivy vulnerability scan (zero Critical/High), non-root user verification, no embedded secrets
   - K8s gates: resource limits defined, liveness/readiness probes configured, Iron Bank base image compliance
2. **Auto-fix**: If any verification gate fails, attempt automated repair — adjust code, configuration, or test fixtures to resolve the failure.
3. **Re-verify**: Run all verification gates again after fixes. Confirm each gate transitions from FAIL to PASS.
4. **Escalate**: If auto-fix fails after 2 attempts, escalate to human reviewer with a complete evidence pack. Include the failing gate identifier, error output, attempted fixes, and root cause hypothesis.

## Artifact Contract

Every stage of this skill produces paired outputs for machine-consumable handoff:

| Stage | Markdown Output | JSON Output |
|-------|----------------|-------------|
| Application Analysis | `app_analysis.md` | `app_analysis.json` |
| Dockerfile Creation | `dockerfile.md` | `dockerfile.json` |
| Kubernetes Manifest Generation | `k8s_manifests.md` | `k8s_manifests.json` |
| Image Scan & Validation | `image_scan.md` | `image_scan.json` |
| Deployment Verification | `deploy_verify.md` | `deploy_verify.json` |

JSON outputs must conform to the schema defined in `audit/artifact-schemas/`. Markdown outputs are the human-readable narrative; JSON outputs are the machine-consumable contract consumed by the next stage or by OpenClaw for artifact validation.

## Evidence Pack

On completion, produce `evidence-pack.json` containing:

```json
{
  "session_id": "<Devin session identifier>",
  "timestamp": "<ISO 8601 completion time>",
  "skill_id": "devinclaw.containerization.v1",
  "artifacts": [
    {
      "filename": "<output file>",
      "sha256": "<SHA-256 hash of file contents>",
      "stage": "<which stage produced this artifact>"
    }
  ],
  "verification": {
    "gates_run": ["<gate_1>", "<gate_2>"],
    "gates_passed": ["<gate_1>", "<gate_2>"],
    "gates_failed": [],
    "auto_fix_attempts": 0,
    "test_summary": {"passed": 0, "failed": 0, "skipped": 0},
    "scan_summary": {"critical": 0, "high": 0, "medium": 0, "low": 0}
  },
  "knowledge_updates": [
    {
      "action": "created|updated",
      "knowledge_id": "<Devin knowledge entry ID>",
      "summary": "<what was learned>"
    }
  ],
  "escalations": [
    {
      "gate": "<failing gate>",
      "reason": "<why auto-fix failed>",
      "evidence": "<link to error output>"
    }
  ]
}
```

## Escalation Policy

- **Divergence threshold**: 0.35 — if parallel verification sessions disagree beyond this threshold on key findings, escalate to human reviewer with both evidence packs for adjudication.
- **Human approval required for**: production deployment approval, resource limit exceptions, base image substitutions, persistent volume provisioning.
- **Auto-escalate on**: Any security finding rated HIGH or CRITICAL, any risk of data loss or corruption, any changes to authentication or authorization logic, any modification to safety-critical code paths (DO-178C applicable systems).

## Forbidden Actions

- Do not use `latest` tag for any base image. Always pin to a specific version (e.g., `eclipse-temurin:17.0.9_9-jre-alpine`).
- Do not run containers as root. Every Dockerfile must include `USER` instruction switching to a non-root user.
- Do not bake secrets, credentials, API keys, certificates, or connection strings into container images. Use runtime injection via environment variables, mounted secrets, or secret store integration.
- Do not skip the Trivy vulnerability scan. Every image must be scanned before PR creation.
- Do not install package managers or build tools in the runtime stage. Use multi-stage builds to keep the runtime image minimal.
- Do not use `COPY . .` without a `.dockerignore` file. This risks including source code, git history, test data, and credentials in the image.
- Do not use `ADD` when `COPY` suffices. `ADD` has implicit tar extraction and URL fetching behavior that introduces unpredictability.
- Do not create Kubernetes manifests without resource limits. Unbounded containers risk noisy-neighbor problems and node-level OOM kills.
- Do not store persistent data inside the container filesystem. Use volumes or external storage.
- Do not skip the SDD specification step. Every containerization unit must have a documented design before Dockerfile creation begins.
- Do not skip the TDD test generation step. Every containerized application must have tests validating container behavior before deployment.
