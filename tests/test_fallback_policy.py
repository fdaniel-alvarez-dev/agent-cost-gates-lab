from cost_gates import BudgetContext, CostGateMiddleware, CostReport, FallbackPolicy


def test_fallback_policy_executes_cheaper_local_tool_after_primary_block() -> None:
    calls: list[str] = []

    def primary(_payload: dict[str, object]) -> dict[str, object]:
        calls.append("primary")
        return {"tool": "primary"}

    def fallback(_payload: dict[str, object]) -> dict[str, object]:
        calls.append("fallback")
        return {"tool": "fallback"}

    budget = BudgetContext(budget_id="fallback", max_cost_micros=500, max_tool_calls=2)
    report = CostReport(
        budget_id=budget.budget_id,
        max_cost_micros=budget.max_cost_micros,
        max_tool_calls=budget.max_tool_calls,
    )
    middleware = CostGateMiddleware(
        budget=budget,
        report=report,
        tools={"primary": primary, "fallback": fallback},
    )
    policy = FallbackPolicy(fallback_tool="fallback", fallback_estimate_micros=100)

    result = policy.execute(
        middleware=middleware,
        primary_tool="primary",
        primary_estimate_micros=900,
    )

    assert result.status == "fallback"
    assert result.output == {"tool": "fallback"}
    assert calls == ["fallback"]
    assert budget.spent_micros == 100
    assert [event.status for event in report.events] == ["blocked", "fallback"]
    assert report.fallback_count == 1
