# Hackathon Live Demo Script — Step-by-Step Presentation

## Sequence (Total Time: ~3-4 Minutes)

### Act 1: Smart API Integration & Documentation (Theme 1 & 2)
1. **Open Overview Tab**: Point out the live KPI metrics (Connected APIs, Generated Tools, Task Reliability).
2. **Click "API Integrations" Tab**:
   - Show the pre-registered **Travel & Booking Sandbox API** (9 operations).
   - Highlight **AI-Readiness Findings**: OpenAPI 3.x valid, mutating endpoints detected, idempotency support checked.
   - Click **"EXPORT INTEGRATION CODE"**: Show generated `client.py`, `tools.json`, and `README.md`.
3. **Click "API Docs" Tab**:
   - Show the contract-derived documentation with **Autonomous Agent Decision Rules** and **Failure & Recovery Guidelines**.
   - Demonstrate **Copy Markdown** and **Download .md**.

### Act 2: Multi-Service Connectivity (Theme 3)
1. **Click "Connectors" Tab**:
   - Explain multi-service coordination: **Flight Discovery** $\rightarrow$ **Reservation** $\rightarrow$ **Payment Gateway**.

### Act 3: Autonomous Agent Crash Test & Failure Diagnosis (The Differentiator)
1. **Click "Crash Tests" Tab**:
   - Scenario: `Timeout After Commit (Fault)`.
   - Agent Policy: `Unsafe Blind Retry`.
   - Click **RUN CRASH TEST**.
   - **Observe Failure**: 2 reservations created (1 duplicate).
   - **Observe Diagnosis**: Isolates `Ambiguous Operation Outcome & Unsafe Blind Retry`, linking HTTP 504 and duplicate POST trace IDs.
   - **Recommendation**: Use `Idempotency-Key` or status recovery.

### Act 4: Safe Remediation & Before/After Comparison
1. Change Retry Policy to: `Idempotent Key (Safe)`.
2. Click **RUN CRASH TEST** $\rightarrow$ **PASS** (1 reservation, 0 duplicates).
3. **Click "Remediation Diff" Tab**:
   - Compare Baseline (Failed) vs Remediated (Passed).
   - Show outcome transition `FAILED -> COMPLETED`, side-effect delta $2 \rightarrow 1$ reservation, and verified remediation efficacy.

### Act 5: Empirical Reliability Analytics
1. **Click "Reliability" Tab**: Show live empirical success percentages derived strictly from actual recorded runs.
