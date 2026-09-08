# Feature Matrix — Agent Crash Test

| Capability Area | Feature | Description | Status |
| :--- | :--- | :--- | :--- |
| **Smart Integration** | OpenAPI Ingestion | Ingests URL, JSON, YAML, or live endpoint | **VERIFIED** |
| | Schema Resolution | Resolves recursive `$ref`, parameters & bodies | **VERIFIED** |
| | Code Generation | Exports `client.py`, `tools.json`, `README.md` | **VERIFIED** |
| | AI-Readiness Analysis | Evaluates idempotency, mutation tags, errors | **VERIFIED** |
| **Connectivity** | Multi-Service Connectors | Coordinates Discovery $\rightarrow$ Booking $\rightarrow$ Payments | **VERIFIED** |
| **Documentation** | AI Documentation Builder | Generates contract-grounded Markdown & HTML | **VERIFIED** |
| | Agent Decision Rules | Encodes explicit autonomous interaction rules | **VERIFIED** |
| **Reliability Testing** | Real HTTP Execution | Executes agent calls via `httpx` async client | **VERIFIED** |
| | Monotonic Trace Log | Captures ordered timeline with payloads | **VERIFIED** |
| | Fault Injection | Simulates 504 timeouts, 422 errors, breaches | **VERIFIED** |
| | Deterministic Evaluator | Inspects state snapshot & task constraints | **VERIFIED** |
| | Failure Diagnosis | Isolates root causes with trace event IDs | **VERIFIED** |
| | Before / After Diff | Proves duplicate reduction & status transition | **VERIFIED** |
| | Empirical Reliability | Dynamically computes percentage from runs | **VERIFIED** |
| **Developer Console** | Unified Dashboard | 7-tab React + Vite + Tailwind testing console | **VERIFIED** |
