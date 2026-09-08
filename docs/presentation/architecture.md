# Architecture Diagram — Presentation Slide Guide

## High-Level System Architecture

```text
                               ┌────────────────────────────────────────┐
                               │   React + Vite Developer Testing UI    │
                               └───────────────────┬────────────────────┘
                                                   │ HTTP / REST
                                                   ▼
                               ┌────────────────────────────────────────┐
                               │       FastAPI Application Engine       │
                               └───────────────────┬────────────────────┘
                                                   │
        ┌──────────────────────────────────────────┼──────────────────────────────────────────┐
        │                                          │                                          │
        ▼                                          ▼                                          ▼
┌───────────────────────┐              ┌───────────────────────┐              ┌───────────────────────┐
│ Smart API Integration │              │   Autonomous Agent    │              │  Contract-Derived AI  │
│      & Analyzer       │              │  Crash Testing Loop   │              │ Documentation Builder │
└──────────┬────────────┘              └───────────┬───────────┘              └───────────────────────┘
           │                                       │
           ▼                                       ▼
┌───────────────────────┐              ┌───────────────────────┐
│  Client & Tool Code   │              │ Dynamic Tool Executor │
│      Generator        │              │  (Real HTTP / httpx)  │
└───────────────────────┘              └───────────┬───────────┘
                                                   │
                                                   ▼
                                       ┌───────────────────────┐
                                       │   Multi-Service API   │
                                       │   Stateful Sandbox    │
                                       └───────────┬───────────┘
                                                   │
                                                   ▼
                                       ┌───────────────────────┐
                                       │ Real-Time Trace Log   │
                                       │ (Monotonic Evidence)  │
                                       └───────────┬───────────┘
                                                   │
                                       ┌───────────┼───────────┐
                                       ▼           ▼           ▼
                                  Evaluation   Diagnosis  Reliability
```
