# Agent Crash Test — Submission Readiness & Validation Report

**Submission Deadline:** March 9, 2026 / Hackathon Evaluation Window  
**Target Repository:** `D:\Hackathons\agent-crash-test`  
**Candidate Commit:** `9267ad5` (with final environment & presentation enhancements)

---

## 1. Project Name
**AGENT CRASH TEST**  
*Autonomous AI Agent API Integration & Reliability Testing Framework*

---

## 2. One-Line Description
An AI-ready API integration and reliability framework that dynamically ingests OpenAPI contracts, generates multi-service connectors and documentation, and empirical crash-tests autonomous agents under real-world failure modes to prevent duplicate side-effects.

---

## 3. Problem Statement Alignment (Problem Statement #4)
Autonomous AI agents are increasingly interacting with production APIs to perform real-world tasks (booking, purchasing, inventory management, provisioning). However:
- **API Integration & Tool Generation is brittle:** Translating raw OpenAPI contracts into reliable LLM tools and multi-service connectors is error-prone.
- **Traditional API Testing is Blind to Agent Failure Modes:** Standard tests verify HTTP 200 responses under happy paths. They fail to test how autonomous agents react to ambiguous timeouts, HTTP 422 parameter rejections, or semantic constraint breaches.
- **Uncontrolled Side Effects:** When an ambiguous timeout occurs after a database commit (e.g., HTTP 504), naive blind retries cause duplicate bookings, duplicate financial debits, and state corruption.

---

## 4. Solution Statement
Agent Crash Test provides an end-to-end framework featuring:
1. **Smart API Integration & Analyzer:** Ingests any OpenAPI 3.x contract, validates AI-readiness (idempotency, schema definitions, mutating vs. read-only endpoints), and exports Python client code + LLM tool specifications.
2. **Multi-Service Connectors:** Manages stateful multi-step workflows (Discovery → Reservation → Payment settlement).
3. **AI Documentation Builder:** Automatically generates contract-grounded API documentation with autonomous agent decision rules and failure recovery guidance.
4. **Autonomous Crash Testing Engine:** Injects deterministic fault scenarios (`normal`, `timeout_after_commit`, `invalid_parameter`, `constraint_violation`), executes agents (deterministic, LLM, violating), records chronological HTTP traces, evaluates ground truth outcomes, diagnoses root causes, and validates before/after remediation efficacy.
5. **Real-time Developer Dashboard:** Visualizes integrations, connectors, live crash traces, diagnosis, before/after diffs, generated docs, and empirical reliability metrics.

---

## 5. Tech Stack
- **Backend:** Python 3.11+ / 3.14, FastAPI, Pydantic v2, HTTPX, Uvicorn
- **Persistence:** SQLAlchemy 2.0 (synchronous engine with asyncpg/psycopg2 driver support for PostgreSQL, SQLite local fallback, in-memory mode)
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Lucide React
- **Testing & Tooling:** Pytest, Pytest-Asyncio, Playwright (Chromium/Edge headless automation)
- **Containerization:** Docker, Docker Compose, Multi-stage Node/Nginx + Python Alpine/Slim builds

---

## 6. IBM Bob Usage Summary
IBM Bob served as an **AI development & engineering partner** throughout the software lifecycle:
- **Planning & Architecture:** Structuring the separation of concerns between OpenAPI tool generation, multi-service connectors, and evaluation pipelines.
- **Implementation Assistance:** Generating initial scaffolding for FastAPI routers, Pydantic schemas, and stateful sandbox routers.
- **Debugging & Root-Cause Analysis:** Resolving SQLite/PostgreSQL schema conversion edge cases and designing monotonic trace sequence indexing.
- **Documentation & Review:** Reviewing code for strict anti-hallucination boundaries and verifying internal document consistency across presentation assets.

*(Note: IBM Bob assisted and accelerated human engineering and review; all code and architectural components have been executed, debugged, and verified).*

---

## 7. GitHub & Repository Readiness
- **Git Branch:** `master`
- **Working Tree:** Clean, verified with zero orphaned files.
- **Documentation:** Complete presentation docs in `docs/presentation/`, Bob logs in `docs/bob/`, failure models in `docs/failure-model.md`.
- **Screenshots:** 10 presentation-quality screenshots saved in `docs/presentation/screenshots/`.

---

## 8. Local Setup & Demo Instructions

### Fast Local Execution (Windows PowerShell / Bash)
```powershell
# 1. Start FastAPI Backend (Port 8000)
.\.venv\Scripts\uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000

# 2. Start Frontend Dev Server (Port 5173)
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```
- Open Dashboard: `http://localhost:5173`
- Backend Swagger Docs: `http://127.0.0.1:8000/docs`

### Automated Full Stack Verification
```powershell
# Run backend pytest suite (30 tests)
.\.venv\Scripts\python.exe -m pytest -v

# Run live E2E verification across all 13 core workflows
.\.venv\Scripts\python.exe scripts\verify_live_e2e.py

# Run generic OpenAPI import verification
.\.venv\Scripts\python.exe scripts\test_generic_openapi.py

# Re-capture dashboard screenshots
.\.venv\Scripts\python.exe scripts\capture_presentation_screenshots.py
```

---

## 9. Feature Verification Status

### A. VERIFIED (Empirically Executed & Tested)
1. **Health Check (`GET /health`):** Returns 200 OK with service name and timestamp.
2. **Dynamic OpenAPI 3.x Ingestion (`POST /integrations`):** Parses arbitrary specs, extracts endpoints, generates `tools.json`, `client.py`, and `README.md`. Tested with both Travel Sandbox and generic Warehouse Inventory API.
3. **Multi-Service State Machine:** Flight Discovery (`GET /sandbox/flights`) → Reservation (`POST /sandbox/reservations`) → Payment Settlement (`POST /sandbox/payments`).
4. **AI Documentation Builder (`GET /documentation/{id}`):** Generates structured markdown docs with parameter tables, sample payloads, and autonomous agent usage rules.
5. **Deterministic & LLM Agent Execution:** Executes multi-step agent loop against sandbox tools with parameter validation and max step safety bounds.
6. **Fault Injection — Ambiguous Timeout (`timeout_after_commit`):** Server commits database mutation, drops network response (HTTP 504); unsafe retry causes duplicate booking detected by evaluation engine.
7. **Safe Remediation Verification (`idempotent_retry`):** Agent uses idempotency keys; duplicate attempt returns cached reservation with zero side effects (`remediation_effective = True`).
8. **Invalid Parameter Recovery (`invalid_parameter`):** HTTP 422 rejected request is analyzed and self-corrected by agent on subsequent retry.
9. **Constraint Violation Evaluation (`constraint_violation`):** Evaluator catches budget breach (e.g., booking exceeds ₹8,000 max price) even when HTTP API returns 200 OK.
10. **Before/After Remediation Comparison (`GET /comparison`):** Computes status transition (`FAILED -> COMPLETED`) and side-effect delta.
11. **Empirical Reliability Analytics (`GET /reliability`):** Dynamically calculates aggregate success rates and per-scenario breakdown from real recorded run data.
12. **State Reset (`POST /admin/demo/reset`):** Clears sandbox state and runs back to nominal defaults.
13. **Dashboard UI (React 18 + Vite):** All 7 tabs (Overview, Integrations, Connectors, Crash Tests, Remediation Diff, API Docs, Reliability) tested and visually captured.
14. **Database Persistence:** SQL schema models verified with SQLAlchemy 2.0 with persistence across independent repository sessions.

### B. PARTIALLY VERIFIED
- **Docker Compose Production Stack:** `docker-compose.yml`, `backend/Dockerfile`, and `frontend/Dockerfile` are verified and configured. On host environments lacking the Windows Subsystem for Linux (WSL2), Docker Engine requires WSL2 or native Linux host; the local Python + Node native stack is fully verified.

### C. NOT VERIFIED / OPTIONAL
- **Live OpenAI API Key Tests (`test_real_openai_compatible_provider_optional`):** Skipped by design when external cloud API keys are omitted; deterministic and mock LLM agent providers run fully locally with 0 external dependencies.

---

## 10. Exact Test Commands & Outcomes

| Test Suite / Script | Command | Result |
| :--- | :--- | :--- |
| **Pytest Unit/Integration Suite** | `python -m pytest -v` | **29 PASSED, 1 SKIPPED (30 total)** |
| **Full Live E2E Verification** | `python scripts/verify_live_e2e.py` | **13/13 Workflows PASSED** |
| **Generic OpenAPI Verification** | `python scripts/test_generic_openapi.py` | **100% Dynamic Spec & Code Gen PASSED** |
| **Frontend Production Build** | `cd frontend; npm run build` | **0 TypeScript Errors, 0 Build Errors** |
| **Playwright Screenshot Capture** | `python scripts/capture_presentation_screenshots.py` | **10/10 Screenshots Captured** |

---

## 11. Captured Presentation Screenshots
All actual screenshots captured from the live dashboard are located in `docs/presentation/screenshots/`:
1. `01-overview.png` — System status, quick actions, metric cards, recent runs.
2. `02-integrations.png` — Discovered integrations, AI readiness analysis, OpenAPI metadata.
3. `03-generated-tools.png` — Generated Python client code and LLM tool schemas.
4. `04-connectors.png` — Multi-service connectors and coordinated workflows.
5. `05-crash-test.png` — Test execution console with fault injection scenario selector.
6. `06-failure-trace.png` — Chronological monotonic HTTP trace with expandable request/response payloads.
7. `07-diagnosis.png` — Root cause failure analysis and remediation recommendations.
8. `08-before-after.png` — Side-by-side before/after remediation diff with side-effect deltas.
9. `09-documentation.png` — AI-generated API documentation with agent decision rules.
10. `10-reliability.png` — Empirical reliability breakdown across fault scenarios.
