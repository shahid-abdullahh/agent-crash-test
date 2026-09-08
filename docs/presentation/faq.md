# Frequently Asked Questions (FAQ) — Presentation Guide

### Q1: How does this align with Problem Statement #4 (Smart API Integration & AI-Ready Connectivity)?
**A**: It covers the complete lifecycle:
1. Ingests API contracts and generates integration tools and client code.
2. Models multi-service connectivity (Discovery $\rightarrow$ Booking $\rightarrow$ Payments).
3. Builds AI-ready API documentation with agent decision rules.
4. Validates whether autonomous agents can actually use those integrations safely in production.

---

### Q2: Why is testing autonomous agents different from standard API testing?
**A**: Standard API tests verify that an API endpoint returns `200 OK` under normal parameters. Autonomous agents make dynamic multi-step decisions, encounter ambiguous timeouts (HTTP 504), and attempt uncoordinated retries that cause catastrophic duplicate side-effects (e.g. double bookings, duplicate charges). Agent Crash Test is the first platform designed specifically to detect, diagnose, and remediate agent-API interaction failures.

---

### Q3: Is the evaluation performed by an LLM?
**A**: **No.** Evaluation is 100% deterministic and independent. The system inspects real HTTP traces and server-side state snapshots to verify criteria and duplicate mutations. The LLM is never the judge of its own task completion.

---

### Q4: How is IBM Bob used in this project?
**A**: IBM Bob is our AI SDLC engineering partner used to plan, implement, debug, review, and document the integration and testing framework across Plan Mode, Agent Mode, Ask Mode, and Review Mode.
