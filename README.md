# Cost Gates for AI Agents

This repository is a small, production-oriented reference implementation for:

**A3: Cost Gates for AI Agents: The Architecture Pattern We Needed Before Scaling Tool Calls**

It demonstrates an offline, deterministic architecture pattern for controlling agent tool calls before execution:

- Budget context with deterministic `cost_micros` accounting.
- Tool-call counter with hard limits.
- Cost gate middleware that blocks unaffordable calls before invoking tools.
- Fallback policy for cheaper deterministic local tools.
- Cost report that shows what was attempted, blocked, executed, and charged.

No real APIs, secrets, live pricing, telemetry, or claimed savings are used. All costs are task-provided estimates used only for gate decisions.

## Quick Start

```bash
python3 -m pytest -o cache_dir=/tmp/agent-cost-gates-lab-pytest-cache
python3 -m ruff check .
python3 -m compileall src tests
python3 -m cost_gates examples/cheap_task.json
python3 -m cost_gates examples/expensive_task_blocked.json
python3 -m cost_gates examples/fallback_triggered.json
```

## Example Output Shape

The CLI prints a text report with:

- Budget limits.
- Total charged deterministic estimate.
- Tool call count.
- Per-step events with `allowed`, `blocked`, or `fallback` status.
- A policy notice that the report is not a real-world savings claim.

## Repository Layout

```text
src/cost_gates/          Python package
examples/                Deterministic task inputs
docs/                    Architecture and policy notes
tests/                   Unit tests
VALIDATION_REPORT.md     Commands run and results
```

## Design Boundary

This lab is intentionally narrow. It is not a billing system, optimizer, observability product, or benchmark. It is a deterministic control-plane pattern for deciding whether a proposed tool call should be allowed before the call happens.
