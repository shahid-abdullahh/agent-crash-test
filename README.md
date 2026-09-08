# Agent Crash Test 💥

> **"Test APIs the way autonomous agents actually use them."**

Agent Crash Test is a developer-facing platform that assigns multi-step tasks to autonomous AI agents, enables controlled interaction with sandboxed APIs, records complete HTTP/agent interaction traces, deterministically evaluates task completion and side-effect safety, diagnoses failure modes with concrete evidence, and calculates empirical reliability metrics.

---

## Current Status (Phase 1 — Core Execution & Evaluation Spine)

## Features & Capabilities

- **Real Agent Execution**: Executes real agent loops against actual HTTP sandbox endpoints (no mock API skips).
- **Dynamic OpenAPI Tool Generation**: Generates standard tool definitions directly from OpenAPI 3.x contracts with `$ref` resolution and JSON schema typing.
- **Provider-Independent Agent**: Pluggable `LLMProvider` interface with support for OpenAI-compatible LLMs and deterministic test doubles.
- **Strict Safety Boundaries**: Tool whitelisting, argument schema validation, step limit protection, and structured action models.
- **Independent Deterministic Evaluation**: Objective sandbox state inspection, constraint verification, and duplicate side-effect detection.
- **Evidence-Based Diagnosis**: Automatically isolates root causes (e.g. Ambiguous Operation Outcome + Unsafe Retry) and links exact trace event IDs.
- **Before/After Remediation Comparison**: Quantifies remediation efficacy (`FAILED -> COMPLETED`, duplicate elimination).
- **Dual-Mode Persistence**: Abstract `TaskRepository` & `RunRepository` with seamless `InMemory` or PostgreSQL / SQLite SQLAlchemy persistence.
- **Developer Testing Console**: Interactive React + Vite + TypeScript + Tailwind developer UI for running crash tests, inspecting traces, reviewing diagnoses, and comparing remediation runs live.

---

## Project Structure

```text
agent-crash-test/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI Application Entrypoint
│   │   ├── api/                     # REST API Endpoints (health, tasks, runs, reliability, comparison)
│   │   ├── db/                      # SQLAlchemy Models & Session Management
│   │   ├── schemas/                 # Pydantic Domain Schemas
│   │   ├── openapi/                 # OpenAPI 3.x Tool Generator
│   │   ├── agent/                   # Agent Abstraction, Deterministic Agent, LLMAgent, & Providers
│   │   ├── sandbox/                 # Stateful Travel API & Scenario Fault Injection
│   │   ├── traces/                  # Structured Trace Collector
│   │   ├── evaluator/               # Deterministic Evaluator
│   │   ├── diagnosis/               # Failure Diagnosis Engine
│   │   └── services/                # Task, Run, Reliability, Comparison, and Repository Services
│   ├── tests/                       # Complete Unit, Integration & Vertical Slice Tests
│   └── requirements.txt
├── frontend/                        # React + Vite + TypeScript + Tailwind Developer Console
├── docs/
│   ├── architecture.md              # System Architecture & Separation of Concerns
│   ├── failure-model.md             # Failure Taxonomy & Invariants
│   ├── demo.md                      # Step-by-Step Hackathon Demo Guide
│   └── bob/                         # IBM Bob Review Logs
├── scripts/
│   └── verify_live_e2e.py           # End-to-End Live Scenario Verification
├── pytest.ini
└── README.md
```

---

## Quickstart

### 1. Setup Backend Environment
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
uvicorn app.main:app --app-dir backend --port 8000
```

### 4. Run Frontend Developer Testing Console
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

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
| `GET` | `/comparison` | Compare baseline vs remediated runs |
