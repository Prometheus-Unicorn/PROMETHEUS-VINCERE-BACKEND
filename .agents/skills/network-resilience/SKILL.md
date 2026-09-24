---
name: network-resilience
description: Manages network fluctuations, intermittent socket timeouts, DNS drops, and broken connections with automated jittered retries, socket recycling, and stateful checkpointing. Use when experiencing network fluctuations, request timeouts, socket disconnects, DNS resolution errors, or when automating headless browser actions over unstable connections.
---

# Network Resilience & Uninterrupted Execution Skill

This skill provides patterns, decorators, and execution managers to ensure automation workflows, API calls, and browser sessions execute continuously and recover automatically despite network drops, high packet loss, or socket timeouts.

## When to Use
- When automation scripts experience timeout errors (`TimeoutError`, `net::ERR_TIMED_OUT`, `net::ERR_NAME_NOT_RESOLVED`, `ConnectionResetError`).
- When network connections fluctuate or drop intermittently during long-running cloud tasks.
- When dispatching browser actions (Playwright CDP, HTTP requests) that must survive transient connectivity loss without crashing the pipeline.

## Core Resilience Pillars

1. **Jittered Exponential Backoff (Decorrelated Jitter)**:
   - Prevents retry storms by randomizing sleep times between $[0, \min(M, B \times 2^i)]$.
   - Fails gracefully only after budget exhaustion, logging clear retry artifacts.

2. **Persistent Checkpointing**:
   - Checkpoints atomic completion states to disk (`.checkpoints/task_<id>.json`).
   - If an unrecoverable failure occurs, the task resumes directly from the last valid step without re-executing completed operations.

3. **Multi-Tier DNS Fallback**:
   - When default router DNS drops resolution for target domains (e.g. `flow.google.com`), automatically falls back to authoritative public resolvers (`8.8.8.8`, `1.1.1.1`).

4. **Self-Healing Browser / CDP Session**:
   - Recovers from browser disconnection by pinging the endpoint, reopening lost contexts, or reconnecting to CDP instead of failing the pipeline.

## Quick Start Pattern

```python
from mini_run_pipeline.resilient_network import resilient_retry, resilient_action

# Async or sync action retry with jittered backoff
@resilient_retry(max_retries=5, initial_backoff=1.0, max_backoff=20.0)
async def fetch_or_execute():
    ...

# Safe Playwright operation that absorbs transient network timeouts
result = await resilient_action(
    lambda: page.goto("https://flow.google.com", timeout=45000),
    max_retries=4,
    retryable_errors=(TimeoutError, Exception),
)
```

## Checklist Before Long-Running Executions
- [ ] Decorated network-bound I/O with `@resilient_retry`.
- [ ] Configured local timeouts to at least 2x average latency under jitter.
- [ ] Enabled checkpoint persistence for multi-stage pipelines.
- [ ] Verified DNS fallback connectivity.
