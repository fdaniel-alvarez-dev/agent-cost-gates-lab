# Cost Model

The lab uses `cost_micros`, an integer accounting unit supplied by the task input.

`cost_micros` is not live provider pricing. It is not a measured invoice amount. It is a deterministic estimate used by the gate to decide whether a tool call is allowed.

## Rules

- Estimates are non-negative integers.
- A call is blocked when `spent_micros + estimate_micros` exceeds `max_cost_micros`.
- A call is blocked when it would exceed `max_tool_calls`.
- Blocked calls are recorded but charged `0`.
- Allowed and fallback calls are charged exactly their supplied estimate.

## Why Integers

Integer accounting avoids floating-point drift and makes tests deterministic. A production system could map `cost_micros` to an internal normalized unit, but the gate should still compare integers or fixed-precision decimals.

## What The Report Means

The report shows deterministic accounting under the declared budget. It does not show real spending, provider billing, avoided spend, or savings.
