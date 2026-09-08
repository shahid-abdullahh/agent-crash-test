# Agent Crash Test — Failure Model & Taxonomy

## 1. Executive Summary

Autonomous AI agents fail differently than traditional deterministic API clients. Traditional clients typically execute fixed workflows with pre-compiled assumptions. Autonomous agents generate dynamic plans, interpret schema documents (e.g. OpenAPI), and self-direct tool execution loops. 

Agent Crash Test defines a rigorous taxonomy of failure modes based on empirical observation of agent-API dynamics.

---

## 2. Failure Classification Matrix

| Failure Category | Trigger Condition | Agent Behavior | Observed API Status | Evaluator Outcome | Primary Remediation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Ambiguous Operation Outcome** | Upstream timeout (HTTP 504) after state mutation committed | Agent executes blind duplicate retry | HTTP 504 followed by HTTP 200 | **FAIL** (Duplicate side-effects detected) | Idempotency-Key headers & Pre-retry status verification |
| **Tool Parameter Validation Failure** | Schema mismatch or carrier format constraint (HTTP 422) | Agent inspects error and self-corrects parameter structure | HTTP 422 followed by HTTP 200 | **PASS** (Self-recovered) | Schema clarification & error payload semantic hints |
| **Constraint Violation / Goal Misalignment** | Agent selects invalid entity (e.g., flight price > task budget) | Agent executes valid tool call with out-of-bounds parameters | HTTP 200 (API Success) | **FAIL** (Task budget constraint breached) | Step-level constraint verification & post-selection validation |
| **Unauthorized Tool Execution** | Agent attempts to invoke tool outside granted whitelist | LLM provider proposes unauthorized tool name | Request Blocked | **FAIL** (Safety boundary triggered) | Strict Tool Authorization Gate & Schema Whitelisting |
| **Max Steps Exhaustion** | Agent enters infinite loop or fails to reach terminal action | Agent exceeds configured step budget (e.g., > 10 steps) | Multiple 200/400s | **FAIL** (Step budget exceeded) | Loop detection & proactive termination |

---

## 3. The Core Invariant: API Success ≠ Task Success

A central design principle of Agent Crash Test is that **an HTTP 200 OK from an API is not proof of task success**.

- If an agent books a ₹9,200 flight when the user gave an ₹8,000 budget constraint, the booking API returns `200 OK`, but the **task failed**.
- If an agent receives a `504 Gateway Timeout` after the backend created a reservation, and blindly issues a second `POST` creating a second reservation, both individual requests might technically be valid, but the **side-effect safety invariant was violated**.

---

## 4. Remediation Dynamics & Before/After Verification

Agent Crash Test does not stop at diagnosis. It provides comparative before-and-after verification:

```text
BASELINE RUN (Injected Fault)
  ↓
DIAGNOSIS (Root Cause Identified: Ambiguous Timeout + Blind Retry)
  ↓
REMEDIATION APPLIED (Idempotency Key / Status Recovery)
  ↓
REMEDIATED RUN
  ↓
COMPARISON (Proves duplicate side-effect reduction: 2 → 1)
```
