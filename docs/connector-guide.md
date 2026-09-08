# Multi-Service Connector Framework Guide

## 1. Overview
The Connector Framework models how autonomous agents connect and coordinate across multiple microservices or API subsystems in real-world workflows.

---

## 2. Multi-Service Workflow Architecture

```text
Flight Discovery Service (GET /flights)
           │
           ▼
Reservation Service (POST /reservations)
           │
           ▼
Payment Gateway Service (POST /payments)
```

1. **Discovery**: Agent queries flight availability matching passenger constraints (Origin, Destination, Budget).
2. **Reservation**: Agent creates a confirmed reservation, allocating seat availability.
3. **Payment Settlement**: Agent submits payment transaction with booking reference and optional idempotency key.

---

## 3. Connector Lifecycle States
- **`CONNECTED`**: Service endpoint registered and reachable.
- **`READY_FOR_TESTING`**: OpenAPI tools generated and authorized for autonomous execution.
- **`TESTED`**: Validated through empirical crash test runs under active fault injection.
