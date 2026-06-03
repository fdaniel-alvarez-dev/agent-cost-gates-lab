# Architecture

The pattern separates agent execution into five deterministic components:

1. `BudgetContext` owns the mutable budget state for one run.
2. `ToolCallCounter` enforces a hard count of tool executions that passed the gate.
3. `CostGateMiddleware` checks a proposed tool call before the tool is invoked.
4. `FallbackPolicy` retries with a configured deterministic fallback when the primary call is blocked.
5. `CostReport` records allowed, blocked, and fallback events.

The control flow is intentionally pre-execution:

```text
agent proposes tool + deterministic estimate
        |
        v
cost gate checks budget and tool-call capacity
        |
        +-- blocked -> record blocked event -> optional fallback
        |
        +-- allowed -> charge estimate -> execute local deterministic tool -> record event
```

## Why Pre-Execution Gates

Agents can choose tool paths dynamically. A cost gate is a middleware boundary that gives the runtime a chance to reject a proposed action before it expands into more work. This is useful even when the cost model is approximate, because the gate is enforcing a declared operating policy rather than predicting real invoices.

## Offline Determinism

This implementation has no network calls, secrets, background telemetry, live provider pricing, or stochastic model behavior. The example tools are local functions. Their estimates come from JSON task files so tests and demos are repeatable.

## Extension Points

Production systems can replace the example local tools with real tool adapters and replace static estimates with a trusted internal estimator. The boundary stays the same: a proposed action must present an estimate and pass the budget context before execution.
