# Agent Crash Test — Live Demo Script & Walkthrough

This document outlines the step-by-step demonstration of **Agent Crash Test** for the IBM SkillUp Hackathon evaluation.

---

## 1. Setup & Launch

1. **Start Backend Server**:
   ```bash
   uvicorn app.main:app --app-dir backend --port 8000
   ```
2. **Start Frontend Console**:
   ```bash
   cd frontend
   npm run dev
   ```
3. Open Developer Testing Console at `http://localhost:5173`.

---

## 2. Demonstration Flow

### Scene 1: Happy Path Execution
1. Select Task: `task-book-cheapest-flight` (Origin: DEL, Dest: BOM, Budget: ≤ ₹8,000, Passenger: Bruce Wayne).
2. Select Scenario: `Normal (Happy Path)`.
3. Agent: `Deterministic Agent`, Policy: `Unsafe Retry`.
4. Click **RUN CRASH TEST**.
5. **Observe**:
   - Status: `COMPLETED`.
   - Evaluation: `100% PASS`.
   - Side Effects: 1 reservation created, 0 duplicates.
   - Trace: 17 ordered trace events captured.

---

### Scene 2: Injected Ambiguous Timeout & Duplicate Side-Effect Failure
1. Change Scenario to: `Timeout After Commit (Fault)`.
2. Agent: `Deterministic Agent`, Policy: `Unsafe Blind Retry`.
3. Click **RUN CRASH TEST**.
4. **Observe**:
   - Status: `FAILED`.
   - Evaluation: `FAIL` (Duplicate side-effect detected).
   - Side Effects: 2 reservations created, 1 duplicate reservation ID recorded.
   - Diagnosis Panel: Identifies `Ambiguous Operation Outcome & Unsafe Blind Retry`, links HTTP 504 and duplicate POST trace event IDs.
   - Recommendation: Use `Idempotency-Key` or query status prior to retry.

---

### Scene 3: Remediation & Before/After Comparison
1. Change Agent Retry Policy to: `Idempotent Key (Safe)`.
2. Click **RUN CRASH TEST**.
3. **Observe**:
   - Status: `COMPLETED`.
   - Side Effects: 1 reservation created, 0 duplicates (Sandbox idempotency matches existing key).
4. Navigate to **Before/After Remediation Comparison Panel**:
   - Baseline Run: Select the failed run from Scene 2.
   - Remediated Run: Select the successful run from Scene 3.
   - Click **COMPARE RUNS**.
   - **Observe**: Outcome transition `FAILED -> COMPLETED`, side-effect delta `2 reservations (1 duplicate) -> 1 clean reservation`, with empirical findings.

---

### Scene 4: API Success ≠ Task Success (Constraint Violation)
1. Select Scenario: `Constraint Violation`.
2. Agent: `Violator` (or retry policy `violating_agent`).
3. Click **RUN CRASH TEST**.
4. **Observe**:
   - Status: `FAILED`.
   - Evaluation: `Price ₹9,200 exceeds budget ₹8,000`.
   - Demonstrates that even when HTTP returns `200 OK`, task evaluator catches the business rule failure.

---

### Scene 5: Parameter Validation & Self-Recovery
1. Select Scenario: `Invalid Parameter Recovery`.
2. Click **RUN CRASH TEST**.
3. **Observe**:
   - Trace shows `HTTP 422 Unprocessable Content` on attempt 1.
   - Agent self-corrects and sends sanitized payload on attempt 2 (`HTTP 200 OK`).
   - Final evaluation: `PASS`.

---

### Scene 6: Empirical Reliability Dashboard
- The header and Reliability Overview update dynamically based strictly on persisted execution runs (no hardcoded metrics).
