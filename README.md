# Agent Crash Test 💥

> **"Test APIs the way autonomous agents actually use them."**

**Official Track**: Developer AI — Problem Statement #4: **Smart API Integration and AI-Ready Connectivity Framework**

---

## Executive Overview

**Agent Crash Test** is an AI-ready API integration and reliability framework that ingests API contracts, generates authorized integration tools and connector artifacts, produces API usage documentation, and then validates whether autonomous AI agents can safely use those integrations to accomplish real multi-step tasks without duplicate side effects.

### The Problem
Traditional API testing asks: *"Does the endpoint return HTTP 200 OK under nominal static inputs?"*

In the modern agentic era, autonomous AI agents operate APIs dynamically. They encounter ambiguous network drops (HTTP 504), receive parameter validation rejections (HTTP 422), and perform uncoordinated blind retries that cause catastrophic duplicate side effects (double bookings, duplicate payment charges).

### The Solution
Agent Crash Test delivers the complete end-to-end framework:
1. **Smart API Integration & Analyzer**: Ingests OpenAPI 3.x specifications (URL, JSON, YAML, or live endpoint), extracts operations, evaluates AI-readiness findings, and generates client libraries and tool schemas.
2. **Multi-Service Connectors**: Coordinates multi-step agent workflows across distributed services (Flight Discovery $\rightarrow$ Reservation $\rightarrow$ Payment Gateway).
3. **AI-Based API Documentation Builder**: Auto-generates contract-derived documentation with explicit autonomous agent decision rules and failure recovery guidelines.
4. **Autonomous Crash Testing Engine**: Injects real-world failure modes, captures chronological HTTP traces, independently evaluates task outcomes, isolates root causes with trace evidence, and verifies before/after remediation efficacy.

---

## Core Product Architecture

```text
                 SMART API INTEGRATION
                         │
             ┌───────────┼───────────┐
             ▼           ▼           ▼
         OpenAPI      Connector    Docs
         Import       Layer       Builder
             │           │           │
             └───────────┼───────────┘
                         ▼
                  AI-READY TOOLS
                         │
                         ▼
                   AGENT TESTING
                         │
                         ▼
              RELIABILITY & SAFETY
```

---

## Problem Statement #4 Mapping

| Problem Statement Theme | Agent Crash Test Implementation | Verified Route / Artifact |
| :--- | :--- | :--- |
| **"Input API details → Create integration code"** | OpenAPI Ingestion & Integration Code Generator (`client.py`, `tools.json`, `README.md`) | `POST /integrations`, `GET /integrations/{id}/code` |
| **"Build connectors between systems"** | Multi-Service Connector Framework (Flight Discovery, Reservation, Payments) | `GET /connectors` |
| **"AI-based API documentation builder"** | Contract-Derived Documentation Builder with Agent Decision Rules | `GET /documentation/{id}` |
| **"AI-Ready Connectivity"** | Automated AI-Readiness Static/Semantic Analysis (Idempotency, Mutation markers, Error models) | `Integration.readiness_findings` |
| **"Agent Safety & Reliability" (Differentiator)** | Autonomous Agent Crash Testing, Trace Capture, Failure Diagnosis, Before/After Diff, Empirical Reliability | `POST /runs`, `GET /comparison`, `GET /reliability` |

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
Open **`http://localhost:5173`** in your browser.

---

## Automated Verification & Docker Compose

### Run 13-Point End-to-End Live Verification
```bash
python scripts/verify_live_e2e.py
```

### Run Full Stack with Docker Compose (PostgreSQL + Backend + Frontend)
```bash
docker-compose up --build
```

---

## API Surface

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Service health status |
| `GET` | `/integrations` | List registered API integrations |
| `POST` | `/integrations` | Ingest and analyze OpenAPI 3.x contract |
| `GET` | `/integrations/{id}/code` | Export generated integration code (`client.py`, `tools.json`, `README.md`) |
| `GET` | `/connectors` | List active multi-service connectors |
| `GET` | `/documentation/{id}` | Generate contract-derived API documentation |
| `GET` | `/sandbox/flights` | Search sandbox flights with filters |
| `POST` | `/sandbox/reservations` | Create flight reservation (stateful) |
| `POST` | `/sandbox/payments` | Process reservation payment (stateful) |
| `GET` | `/tasks` | List all evaluation tasks |
| `POST` | `/runs` | Execute autonomous agent crash test run |
| `GET` | `/runs/{run_id}/trace` | Retrieve complete ordered trace events |
| `GET` | `/runs/{run_id}/evaluation`| Retrieve deterministic evaluation results |
| `GET` | `/runs/{run_id}/diagnosis` | Retrieve structured failure diagnosis |
| `GET` | `/comparison` | Compare baseline vs remediated runs |
| `GET` | `/reliability` | Retrieve empirical reliability metrics |
| `POST` | `/admin/demo/reset` | Reset demo state and recorded runs |

---

## Documentation Index

- [Problem Statement Alignment](docs/problem-statement-alignment.md)
- [Architecture & Separation of Concerns](docs/architecture.md)
- [Smart Integration & Code Generator Guide](docs/integration-guide.md)
- [Multi-Service Connector Framework Guide](docs/connector-guide.md)
- [AI Documentation Builder Guide](docs/api-documentation.md)
- [Failure Model & Taxonomy](docs/failure-model.md)
- [Live Hackathon Demo Walkthrough](docs/demo.md)
- [Local Development & Docker Setup](docs/local-development.md)
- [IBM Bob SDLC Usage & Capability Log](docs/bob/bob-usage.md)
- [Presentation Slide Support Artifacts](docs/presentation/project-abstract.md)
