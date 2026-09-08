# IBM Bob SDLC Usage — Presentation Slide Guide

## How IBM Bob Was Used in Agent Crash Test

### 1. Plan Mode
- Planned the architectural separation between OpenAPI Smart Integration, Connectors, AI Documentation Builder, and the Reliability Evaluation Engine.

### 2. Agent Mode
- Constructed modular domain services (`IntegrationService`, `DocumentationService`) and FastAPI routers.
- Engineered multi-service stateful sandbox models (Flights, Reservations, Payments).

### 3. Ask Mode
- Analyzed and resolved circular import dependencies during module startup.
- Evaluated database persistence boundaries to maintain in-memory fallbacks.

### 4. Review Mode
- Conducted forensic code reviews across all 13 claims, asserting strict anti-hallucination boundaries.
