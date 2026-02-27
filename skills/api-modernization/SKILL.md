---
name: api-modernization
description: Modernize legacy API architectures — SOAP/XML to REST, REST to GraphQL, monolith to microservices. Use this skill when decomposing enterprise onolithic services, converting SOAP/XML endpoints (data standard, notification, data exchange) to REST or GraphQL, migrating REST APIs to GraphQL for efficient data fetching, or breaking apart tightly coupled service architectures into bounded microservices.
---

# API Modernization

## Overview

This skill systematically modernizes legacy API architectures across three migration vectors: SOAP/XML to REST, REST to GraphQL, and monolith to microservices. It handles the full lifecycle from API discovery and contract analysis through implementation, testing, and traffic cutover. The skill leverages DeepWiki MCP for codebase understanding, generates OpenAPI/GraphQL specifications before implementation, and can spawn parallel Devin sessions for large-scale API fleet modernization.

Enterprises operate hundreds of SOAP/XML services across the mission-critical systems . Critical data exchange formats — data standard (Enterprise Data Exchange Model), notification (Enterprise Notifications), and data exchange (Enterprise Data Exchange) — are predominantly SOAP/XML-based. These services suffer from verbose payloads, tight coupling, poor developer ergonomics, and difficulty integrating with modern frontends and mobile platforms. Modernization to REST and GraphQL reduces payload size by 40-70%, improves developer velocity, and enables the enterprise to expose enterprise data through modern API gateways with proper rate limiting, versioning, and observability.

## What's Needed From User

- **Existing API inventory**: WSDL files, OpenAPI/Swagger specs, or endpoint URLs for the services to modernize.
- **Target architecture**: Which migration vector(s) to apply — SOAP→REST, REST→GraphQL, monolith→microservices, or a combination.
- **Service boundaries** (for monolith decomposition): Domain knowledge or bounded context definitions, or permission to derive them from codebase analysis.
- **Data format specifications**: XSD schemas for XML-based services (data standard, notification, data exchange), or sample request/response payloads.
- **Authentication requirements**: Current auth mechanism (WS-Security, OAuth, API keys, mutual TLS) and target auth model.
- **Traffic and SLA data** (optional): Current request volumes, latency requirements, and availability SLAs to inform capacity planning.
- **Consumer inventory** (optional): Known API consumers so call-site migration can be coordinated.
- **Target runtime**: Preferred language/framework for new services (e.g., Spring Boot, Express, FastAPI, Go).

## Procedure

1. **Index existing APIs with DeepWiki**
   - Import all WSDL files, XSD schemas, OpenAPI specs, and API source code into DeepWiki.
   - Build a service dependency graph: which services call which, shared data models, and transitive dependencies.
   - Identify all SOAP operations, REST endpoints, data transfer objects, and message formats.
   - Map XML namespaces and schema imports to understand the full data model hierarchy.
   - Record total endpoint count, estimated request volumes (from logs if available), and data model complexity.

2. **Inventory endpoints and classify migration complexity**
   - Create an inventory of every endpoint/operation with:
     - Service name, operation/endpoint, HTTP method (if REST), SOAP action (if SOAP).
     - Request/response payload schemas with field count and nesting depth.
     - Dependencies on other services, databases, message queues, or external systems.
     - Authentication and authorization requirements per endpoint.
     - Complexity rating: Simple (1:1 mapping, stateless), Moderate (requires data model restructuring or aggregation), Complex (requires service decomposition, stateful orchestration, or protocol bridging).
   - For monolith decomposition: identify bounded contexts using domain-driven design analysis of the codebase, database schema coupling, and transaction boundaries.
   - Flag endpoints with no clean modernization path that require architectural redesign.

3. **Generate SDD specification for each migration unit**
   - For each service or endpoint group, produce a Software Design Document that specifies:
     - Current API contract (WSDL/OpenAPI) and business purpose.
     - Target API contract (OpenAPI 3.1 for REST, GraphQL SDL for GraphQL).
     - Data model transformations: XML complex types to JSON schemas, SOAP faults to HTTP error responses, WS-Security to OAuth 2.0/JWT.
     - For SOAP→REST: HTTP method mapping (SOAP operations to GET/POST/PUT/DELETE), URL structure design, query parameter extraction from XML request bodies.
     - For REST→GraphQL: Query/mutation/subscription design, resolver architecture, DataLoader patterns for N+1 prevention, schema stitching or federation strategy.
     - For monolith→microservices: Service boundary definitions, inter-service communication patterns (sync REST/gRPC vs async messaging), data ownership per service, saga patterns for distributed transactions.
     - Backward compatibility strategy: API versioning, facade/adapter layer, traffic migration plan.

4. **Generate TDD test plans and test cases**
   - For each migration unit, create tests that:
     - Validate functional equivalence between old and new API contracts (same inputs produce semantically equivalent outputs).
     - Test all HTTP status codes and error conditions for REST endpoints.
     - Test GraphQL query depth limits, complexity analysis, and N+1 query prevention.
     - Validate authentication and authorization enforcement on every endpoint.
     - Test backward compatibility through the facade layer (old clients must continue working during migration).
     - Load test critical endpoints against documented SLA thresholds.
   - Contract tests must be runnable against both legacy and modernized endpoints for A/B validation.

5. **Execute SOAP-to-REST migration**
   - Parse WSDL files and extract all operations, port types, bindings, and message definitions.
   - Map SOAP operations to RESTful resources:
     - `getAirport` → `GET /airports/{id}`
     - `searchnotification` → `GET /notams?location={loc}&effective={date}`
     - `submitWorkOrder` → `POST /work-orders`
     - `updateResource` → `PUT /resources/{id}`
     - `cancelnotification` → `DELETE /notams/{id}`
   - Convert XSD complex types to JSON Schema definitions.
   - Replace SOAP envelope/header/body structure with HTTP headers and JSON request/response bodies.
   - Map SOAP faults to HTTP error responses with RFC 7807 Problem Details format.
   - Replace WS-Security with OAuth 2.0 Bearer tokens or mutual TLS as appropriate.
   - Generate OpenAPI 3.1 specification for every new REST endpoint.
   - Implement a SOAP-to-REST facade/proxy for backward compatibility during cutover.

6. **Execute REST-to-GraphQL migration**
   - Analyze existing REST endpoints and their response schemas to design the GraphQL type system.
   - Define GraphQL SDL schema:
     - Map REST resources to GraphQL types.
     - Map GET endpoints to queries, POST/PUT/DELETE to mutations.
     - Identify real-time data needs and define subscriptions.
   - Implement resolvers with DataLoader batching to prevent N+1 query patterns.
   - Configure query complexity analysis and depth limiting to prevent abuse.
   - Implement persisted queries for production security (disable arbitrary queries).
   - Set up schema federation if multiple services contribute to the graph (Apollo Federation or similar).
   - Generate GraphQL introspection documentation.

7. **Execute monolith-to-microservices decomposition**
   - Identify bounded contexts through:
     - Database table clustering analysis (which tables are always queried together).
     - Code module dependency analysis (which packages have minimal cross-references).
     - Business capability mapping (align services to enterprise rganizational functions).
   - Extract services one at a time using the Strangler Fig pattern:
     - Create the new microservice with its own repository, build pipeline, and database.
     - Implement the API contract (REST or GraphQL) for the extracted domain.
     - Route traffic through a facade that delegates to either the monolith or the new service.
     - Migrate consumers incrementally.
     - Decommission the monolith's implementation of that domain once all traffic is migrated.
   - Implement inter-service communication:
     - Synchronous: REST or gRPC with circuit breakers, retries, and timeouts.
     - Asynchronous: Event-driven messaging (Kafka, RabbitMQ, or SQS) for eventual consistency.
   - Implement distributed tracing (OpenTelemetry) across all services.
   - Define health check endpoints (`/health`, `/ready`) for each service.

8. **Run tests and validate**
   - Execute all TDD test cases against modernized APIs.
   - Run contract tests comparing legacy and modernized endpoint responses for functional equivalence.
   - Validate authentication and authorization on every endpoint.
   - Execute load tests against SLA thresholds.
   - For GraphQL: validate query complexity limits, depth restrictions, and DataLoader batching.
   - For microservices: test circuit breaker behavior, retry logic, and graceful degradation.
   - Fix any failures and re-run until all tests pass.
   - Document any intentional behavioral differences (e.g., pagination changes, date format normalization).

9. **Spawn parallel Devin sessions for large API fleets**
   - For modernization campaigns with >10 services, create migration batches grouped by dependency order (leaf services first, gateway services last).
   - Spawn parallel Devin sessions (one per service or logical group) using the Devin API v3 batch endpoint.
   - Each session receives: the SDD spec, TDD test plan, source API artifacts (WSDL/OpenAPI), and the target architecture definition.
   - Monitor all sessions for completion and collect results.
   - Validate cross-service integration after all sessions complete (end-to-end API gateway tests).

10. **Create pull requests and invoke Devin Review**
    - Create one PR per service or logical migration unit.
    - PR description must include: migration vector (SOAP→REST, REST→GraphQL, or monolith→micro), endpoints converted, OpenAPI/GraphQL schema diff, test results, and traffic cutover plan.
    - Invoke Devin Review on each PR for automated quality checks.
    - Address any review findings before merging.

## Specifications

- **OpenAPI version**: All REST API specifications must use OpenAPI 3.1 format.
- **GraphQL specification**: GraphQL schemas must use the June 2018+ specification with SDL syntax.
- **HTTP methods**: Follow RFC 7231 semantics strictly — GET for reads, POST for creation, PUT for full replacement, PATCH for partial update, DELETE for removal.
- **URL design**: Use lowercase kebab-case for URL path segments (`/work-orders`, not `/WorkOrders`). Use plural nouns for collections.
- **Error format**: All REST error responses must use RFC 7807 Problem Details (`application/problem+json`).
- **Versioning**: APIs must be versioned via URL path prefix (`/v1/`, `/v2/`) or `Accept` header. No breaking changes without version bump.
- **Pagination**: All collection endpoints must support pagination. Use cursor-based pagination for GraphQL; offset/limit or cursor for REST.
- **Rate limiting**: All endpoints must include `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `X-RateLimit-Reset` headers.
- **CORS**: Configure CORS headers for browser-based consumers. Default to restrictive allowlist.
- **Content negotiation**: REST endpoints must support `application/json`. XML support (`application/xml`) required for data standard/notification backward compatibility during transition.
- **GraphQL complexity**: Maximum query depth of 10, maximum complexity score of 1000. Enforce via middleware.
- **Batch size**: When using parallel Devin sessions, limit to 10 concurrent sessions per modernization run.
- **Backward compatibility**: Legacy SOAP endpoints must remain operational behind a facade until all consumers have migrated. Minimum 90-day parallel operation period.
- **Test coverage**: Every modernized endpoint must have at least one test case per HTTP method, per status code. Target minimum 80% branch coverage.
- **HATEOAS**: REST responses should include hypermedia links for discoverability where appropriate.

## Advice and Pointers

- data standard and notification XML schemas are deeply nested (10+ levels). Do not attempt a 1:1 JSON mapping. Flatten the structure to 3-4 levels max, using references (`$ref`) for shared components. The enterprise ata exchange program office has published simplified JSON profiles — use those as the starting point.
- SOAP services often have implicit state in WS-Security headers and SOAP sessions. Ensure all state is made explicit in REST (via tokens, query parameters, or request bodies) or GraphQL (via context).
- When decomposing monoliths, resist the temptation to create too many microservices. A common enterprise nti-pattern is splitting too aggressively, creating a distributed monolith. Start with 3-5 coarse services aligned to business capabilities, then split further only when justified by independent deployment needs.
- For GraphQL, always implement DataLoader from day one. N+1 queries against enterprise databases (which are often large and geographically distributed) will cause unacceptable latency.
- SOAP services frequently use document/literal wrapped style, which maps cleanly to REST POST bodies. RPC/encoded style requires more transformation work — flag these during inventory.
- enterprise ervices often have strict availability requirements (99.99% for mission-critical). Plan the traffic cutover as a gradual canary deployment, not a big-bang switch.
- WS-Security to OAuth 2.0 migration is the highest-risk transformation. Map it early, test it exhaustively, and coordinate with the enterprise identity provider team.
- Do not underestimate XML namespace complexity. data standard uses multiple namespaces (aixm, gml, xlink) and namespace-qualified attributes. Ensure the JSON representation preserves semantic meaning even without namespaces.
- Use API gateways (Kong, AWS API Gateway, or Apigee) as the facade layer during migration. They handle routing, versioning, rate limiting, and protocol translation in one place.


## Self-Verification Loop (Devin 2.2)

After completing the primary procedure:

1. **Self-verify**: Run all applicable verification gates:
   - Build/test gates: new API endpoints compile, contract tests pass, backward compatibility verified
   - Security gates: authentication/authorization on all new endpoints, TLS configuration, CORS policy
   - Integration gates: consumer smoke tests against new API, load test results within SLA
2. **Auto-fix**: If any verification gate fails, attempt automated repair — adjust code, configuration, or test fixtures to resolve the failure.
3. **Re-verify**: Run all verification gates again after fixes. Confirm each gate transitions from FAIL to PASS.
4. **Escalate**: If auto-fix fails after 2 attempts, escalate to human reviewer with a complete evidence pack. Include the failing gate identifier, error output, attempted fixes, and root cause hypothesis.

## Artifact Contract

Every stage of this skill produces paired outputs for machine-consumable handoff:

| Stage | Markdown Output | JSON Output |
|-------|----------------|-------------|
| API Inventory | `api_inventory.md` | `api_inventory.json` |
| Contract Design | `contract_design.md` | `contract_design.json` |
| Implementation | `implementation.md` | `implementation.json` |
| Consumer Migration | `consumer_migration.md` | `consumer_migration.json` |
| Traffic Cutover Plan | `cutover_plan.md` | `cutover_plan.json` |

JSON outputs must conform to the schema defined in `audit/artifact-schemas/`. Markdown outputs are the human-readable narrative; JSON outputs are the machine-consumable contract consumed by the next stage or by OpenClaw for artifact validation.

## Evidence Pack

On completion, produce `evidence-pack.json` containing:

```json
{
  "session_id": "<Devin session identifier>",
  "timestamp": "<ISO 8601 completion time>",
  "skill_id": "devinclaw.api_modernization.v1",
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
- **Human approval required for**: legacy endpoint decommissioning, traffic cutover scheduling, WS-Security to OAuth 2.0 migration, data exchange interface changes.
- **Auto-escalate on**: Any security finding rated HIGH or CRITICAL, any risk of data loss or corruption, any changes to authentication or authorization logic, any modification to safety-critical code paths (DO-178C applicable systems).

## Forbidden Actions

- Do not shut down or modify legacy SOAP/REST endpoints until all consumers have been migrated and the 90-day parallel operation period has elapsed.
- Do not skip the SDD specification step. Every migration unit must have a documented design and target contract before code conversion begins.
- Do not skip the TDD test generation step. Every migration unit must have tests before implementation.
- Do not expose GraphQL introspection in production. Use persisted queries and disable introspection behind a feature flag.
- Do not create microservices that share a database. Each service must own its data. Use APIs or events for cross-service data access.
- Do not introduce synchronous inter-service calls for operations that can tolerate eventual consistency. Use asynchronous messaging for non-critical-path communication.
- Do not hardcode service URLs. Use service discovery or configuration management for all inter-service communication.
- Do not bypass the API gateway for service-to-service calls in production. All external traffic must route through the gateway; internal traffic may use direct service mesh routing.
- Do not remove XML content type support for data standard/notification endpoints until the data exchange program office has confirmed all downstream consumers support JSON.
- Do not ignore SOAP WS-Policy attachments. They contain security, transaction, and reliability requirements that must be preserved in the modernized architecture.
