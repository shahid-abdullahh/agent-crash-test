# IBM Bob Architecture & Review Log

This document records the architecture reviews, validation analyses, and engineering decisions evaluated using IBM Bob for the Agent Crash Test hackathon project.

---

## Log Entry 1: Core Execution Separation & Anti-Hallucination Boundaries

- **Date**: 2026-09-08
- **Task**: Architecture review of the execution chain and deterministic evaluation separation.
- **Prompt**:
  > Review the separation of concerns between raw execution observation, deterministic evaluation, failure diagnosis, and empirical reliability calculation. Ensure that the LLM agent is never the judge of its own task completion or side-effect safety.
- **Result**:
  - Confirmed the necessity of keeping Evaluator logic completely deterministic and decoupled from LLM output.
  - Recommended capturing request-response pairs as structured `HTTPPayload` trace events with duration and status code to enable precise root-cause diagnosis.
- **Human Review**: Accepted without modification.
- **Final Implementation Change**: Implemented `Evaluator`, `TraceCollector`, and `DiagnosisEngine` as isolated, deterministic modules in `backend/app/evaluator/`, `backend/app/traces/`, and `backend/app/diagnosis/`.

---

## Log Entry 2: Dual Persistence Strategy & Repository Interfaces

- **Date**: 2026-09-08
- **Task**: Review of PostgreSQL persistence integration without introducing hard coupling or breaking in-memory development workflows.
- **Prompt**:
  > Review the repository interface pattern to allow dual-mode operation: Async SQLAlchemy / SQLite / PostgreSQL persistence when `DATABASE_URL` is configured, falling back seamlessly to `InMemoryTaskRepository` and `InMemoryRunRepository` when unconfigured.
- **Result**:
  - Confirmed that business logic services (`RunService`, `TaskService`, `ComparisonService`) should only depend on abstract `TaskRepository` and `RunRepository` interfaces.
  - Recommended JSON/JSONB column types for complex event payloads and criteria lists to avoid brittle schema migrations across test runs.
- **Human Review**: Accepted.
- **Final Implementation Change**: Created `SQLTask`, `SQLRun`, `SQLTraceEvent`, `SQLEvaluation`, `SQLDiagnosis` models in `backend/app/db/models.py` and dual-mode repositories in `backend/app/services/repository.py`.

---

## Log Entry 3: Before/After Remediation Comparison Model

- **Date**: 2026-09-08
- **Task**: Review of the before/after remediation comparison schema and differential calculation logic.
- **Prompt**:
  > Design a structured comparison contract between a failed baseline run and a remediated run that quantifies side-effect reduction, status transitions, and empirical findings without hardcoded assertions.
- **Result**:
  - Provided structured schema containing `baseline_run`, `remediated_run`, `status_transition`, `side_effect_delta`, and `remediation_effective`.
- **Human Review**: Accepted and integrated into FastAPI routes and React developer console.
- **Final Implementation Change**: Implemented `ComparisonService` in `backend/app/services/comparison_service.py`, `GET /comparison` in `backend/app/api/comparison.py`, and `BeforeAfterComparisonPanel.tsx` in `frontend/src/components/`.
