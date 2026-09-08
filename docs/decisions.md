# Architecture Decision Records (ADRs)

## ADR 1: FastAPI for Backend & Sandbox Routing
- **Decision**: Use FastAPI with Pydantic v2 schemas.
- **Rationale**: Provides automatic OpenAPI documentation, asynchronous I/O support for non-blocking HTTP tool executions, and rapid testability with `httpx.ASGITransport`.

## ADR 2: In-Memory Repository with Clean Abstraction First
- **Decision**: Decouple domain services from the database using `TaskRepository` and `RunRepository` abstractions with in-memory backing for Phase 1.
- **Rationale**: Enables rapid vertical slice validation without database provisioning bottlenecks, while leaving a clean path for PostgreSQL repository implementation.

## ADR 3: Deterministic Agent Test Double
- **Decision**: Build an explicit `BaseAgent` abstraction with a `DeterministicTravelAgent` capable of both `unsafe_retry` and `idempotent_retry` policies.
- **Rationale**: Automated unit and integration tests must run deterministically in CI without incurring external LLM API costs or flake.

## ADR 4: Real HTTP Communication for Tool Execution
- **Decision**: Tools communicate with the sandbox via real HTTP requests (`httpx`), rather than direct internal Python function calls.
- **Rationale**: Real agent crashes arise from HTTP network semantics, partial failures, timeouts, and status codes. Testing Python in-process calls would hide these failure modes.

## ADR 5: Deterministic, Evidence-Grounded Evaluation & Diagnosis
- **Decision**: Avoid using an LLM prompt as the sole evaluator. Inspect sandbox state mutations, side-effects, and trace timestamps directly.
- **Rationale**: Guarantees reproducibility, avoids hallucinated pass/fail judgments, and links diagnosis directly to recorded event IDs.

## ADR 6: Dynamic OpenAPI 3.x Tool Generation
- **Decision**: Generate `ToolDefinition` instances directly from OpenAPI 3.x specifications via `OpenAPIToolGenerator`.
- **Rationale**: Removes hardcoded tool-to-route maps, enabling dynamic tool generation for any OpenAPI-compliant API.

## ADR 7: Provider-Independent LLM Agent & Structured Action Contract
- **Decision**: Implement `LLMProvider` returning validated `AgentAction` instances (`tool_call` or `final`).
- **Rationale**: Decouples the decision loop from model vendors. The `LLMAgent` enforces tool authorization and parameter validation before dispatching to `ToolExecutor`.
