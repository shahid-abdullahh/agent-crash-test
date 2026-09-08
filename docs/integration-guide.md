# Smart API Integration & Code Generator Guide

## 1. Overview
The Integration Generator transforms any standard OpenAPI 3.x contract into ready-to-use client libraries, agent tool definitions, and AI-readiness findings.

---

## 2. Ingestion Methods
You can register an API contract via:
1. **Live Sandbox**: Pre-registered Travel & Payment API on `http://127.0.0.1:8000/sandbox`.
2. **OpenAPI URL**: Supply a remote URL serving OpenAPI JSON or YAML (e.g., `https://api.example.com/openapi.json`).
3. **Pasted Content**: Paste raw JSON or YAML schema strings directly into the Developer Console modal.

---

## 3. Generated Integration Artifacts
When an API is registered, the system creates:
1. **`client.py`**: An asynchronous Python client wrapper implementing typed methods for all discovered operations.
2. **`tools.json`**: Standardized JSON tool specifications with parameter types and schema definitions.
3. **`README.md`**: Quickstart integration guide detailing base URLs, operation tables, and code snippets.

---

## 4. AI-Readiness Evaluation Checks
The analyzer inspects:
- **Contract Schema Quality**: Confirms OpenAPI 3.x structure and parameter definitions.
- **State-Changing Mutating Operations**: Identifies POST, PUT, DELETE, PATCH operations.
- **Idempotency Readiness**: Checks whether mutating endpoints define client-supplied `Idempotency-Key` parameters to prevent duplicate mutations.
- **Error Observability**: Verifies presence of structured 4xx/5xx response models for agent recovery reasoning.
