# Agent Crash Test 💥

> **"Test APIs the way autonomous agents actually use them."**

Agent Crash Test is a developer-facing platform that assigns multi-step tasks to autonomous AI agents, enables controlled interaction with sandboxed APIs, records complete HTTP/agent interaction traces, deterministically evaluates task completion and side-effect safety, diagnoses failure modes with concrete evidence, and calculates empirical reliability metrics.

---

## Current Status (Phase 1 — Core Execution & Evaluation Spine)

- **Backend**: FastAPI modular application with clean separation of services, schemas, and API routes.
- **Controlled Sandbox**: Stateful travel API (`/sandbox/flights`, `/sandbox/reservations`, `/sandbox/state`) supporting deterministic state tracking and fault injection (`timeout_after_commit`).
- **Agent Abstraction**: `BaseAgent` interface and `DeterministicTravelAgent` supporting configurable retry policies (`unsafe_retry`, `idempotent_retry`).
- **Tool Executor**: Real HTTP-driven tool execution via `httpx`.
- **Trace Collector**: Structured event collector with monotonic sequence numbering, request/response tracking, duration metrics, and error logging.
- **Deterministic Evaluator**: Verifies budget constraints, passenger information, and sandbox side-effect safety (detecting duplicate reservations and state corruption).
- **Diagnosis Engine**: Identifies ambiguous timeout & unsafe blind retry failures, returning concrete remediation recommendations and linking evidence trace IDs.
- **Reliability Engine**: Calculates task reliability derived strictly from recorded execution runs.

---

## Project Structure

```text
agent-crash-test/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI Application Entrypoint
│   │   ├── api/                     # REST API Endpoints (health, tasks, runs, reliability)
│   │   ├── schemas/                 # Pydantic Domain Schemas
│   │   ├── sandbox/                 # Stateful Travel API & Scenario Injection
│   │   ├── agent/                   # Agent Abstraction & Deterministic Agent
│   │   ├── traces/                  # Structured Trace Collector
│   │   ├── evaluator/               # Deterministic Evaluator
│   │   ├── diagnosis/               # Failure Diagnosis Engine
│   │   └── services/                # Task, Run, and Reliability Services
│   ├── tests/                       # Complete Unit & Vertical Slice Tests
│   └── requirements.txt
├── docs/
│   ├── architecture.md              # System Architecture & Component Interactions
│   └── decisions.md                 # Architecture Decision Records (ADRs)
├── pytest.ini
├── .gitignore
└── README.md
```

---

## Quickstart

### 1. Setup Environment
```bash
# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\activate  # Windows
source .venv/bin/activate # Linux/macOS

# Install dependencies
pip install -r backend/requirements.txt
```

### 2. Run Test Suite
```bash
python -m pytest -v
```

### 3. Run FastAPI Backend Server
```bash
uvicorn app.main:app --app-dir backend --reload --port 8000
```

### 4. Explore Interactive API Docs
Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser to inspect and trigger API endpoints.

---

## API Surface

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Service health status |
| `GET` | `/sandbox/flights` | Search sandbox flights with filters |
| `POST` | `/sandbox/reservations` | Create flight reservation (stateful) |
| `GET` | `/sandbox/state` | Inspect current sandbox state snapshot |
| `GET` | `/tasks` | List all evaluation tasks |
| `POST` | `/tasks` | Register a new evaluation task |
| `POST` | `/runs` | Execute an agent task run against a scenario |
| `GET` | `/runs/{run_id}` | Retrieve run status and outcome |
| `GET` | `/runs/{run_id}/trace` | Retrieve complete ordered trace events |
| `GET` | `/runs/{run_id}/evaluation`| Retrieve deterministic evaluation results |
| `GET` | `/runs/{run_id}/diagnosis` | Retrieve structured failure diagnosis |
| `GET` | `/reliability` | Retrieve reliability metrics calculated from runs |
