# Empirical Reliability Metrics — Presentation Guide

## 1. What We Measure
Unlike traditional testing that reports static assertions, Agent Crash Test computes empirical task reliability:

$$\text{Task Reliability (\%)} = \left( \frac{\text{Successful Autonomous Task Runs}}{\text{Total Task Runs Executed}} \right) \times 100$$

---

## 2. Invariant Safety Guarantees
1. **At-Most-Once Mutation Safety**: Evaluates duplicate side-effects (duplicate reservations, double payment charges).
2. **Task Goal Completion**: Asserts that passenger information and budget constraints are satisfied.
3. **Trace Groundedness**: Every pass/fail determination is backed by monotonic event traces and sandbox state snapshots. Zero AI hallucination.
