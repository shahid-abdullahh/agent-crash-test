# Agent Crash Test — Architecture

## 1. System Overview

Agent Crash Test evaluates autonomous AI agents by testing APIs the way autonomous agents actually interact with them in real multi-step workflows.

```text
TASK (Objectives & Constraints)
  ↓
AGENT RUNNER (Decision Loop)
  ↓
TOOL EXECUTOR (HTTP Client / Sandbox Bridge)
  ↓
CONTROLLED SANDBOX (Stateful Travel API with Fault Injection)
  ↓
TRACE COLLECTOR (Monotonic Event Stream)
  ↓
DETERMINISTIC EVALUATOR (State & Constraint Verification)
  ↓
FAILURE DIAGNOSIS ENGINE (Root Cause & Remediation)
  ↓
RELIABILITY ENGINE (Empirical Reliability derived from Runs)
```

---

## 2. Core Separation of Concerns

1. **Observation (Trace Collector)**:
   - Captures raw execution evidence (`agent_start`, `agent_thinking`, `tool_call`, `http_request`, `http_response`, `tool_result`, `agent_output`, `error`).
   - Monotonic sequence numbering and precise HTTP request/response payloads.

2. **Sandbox & State (Controlled Travel API)**:
   - Stateful in-memory domain maintaining flights, seats, reservations, and idempotency status.
   - Fault injection engine supporting scenarios such as `normal` and `timeout_after_commit`.

3. **Agent Interface (BaseAgent & Deterministic Agent)**:
   - Separates agent decision making from tool execution.
   - Deterministic test agent models realistic tool invocation policies (`unsafe_retry` vs `idempotent_retry`).

4. **Evaluation (Deterministic Evaluator)**:
   - Inspects sandbox state snapshot, trace events, and task constraints.
   - Evaluates side-effect safety (e.g. duplicate mutations) and criteria pass/fail states.

5. **Diagnosis (Failure Diagnosis Engine)**:
   - Identifies failure patterns (such as Ambiguous Timeout followed by Blind Unsafe Retry).
   - Generates actionable remediation recommendations backed by event IDs.

6. **Persistence Strategy**:
   - `TaskRepository` and `RunRepository` abstraction interfaces.
   - In-memory implementation for high-speed local testing, ready for PostgreSQL backend adapter.
