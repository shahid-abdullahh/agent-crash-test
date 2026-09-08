# AI-Based API Documentation Builder Guide

## 1. Overview
The Documentation Builder analyzes registered OpenAPI contracts and generates rich developer documentation designed specifically for human engineers and autonomous AI agent workflows.

---

## 2. Key Features
1. **Endpoint Signatures & Parameters**: Complete tables detailing method, path, parameter locations (`query`, `path`, `header`, `body`), requirement tags, and JSON schemas.
2. **Request / Response Examples**: Sample payloads generated directly from schema models.
3. **Autonomous Agent Decision Rules**: Explains how AI agents should interact with each endpoint (e.g. read-only vs state-mutating).
4. **Failure & Recovery Considerations**: Highlights common error codes (422 validation, 504 timeouts) and safe recovery practices (querying status before repeating mutations).
5. **Interactive Export**: Built-in Copy Markdown and Download `.md` export capabilities.
