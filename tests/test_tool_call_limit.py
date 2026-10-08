import pytest

from cost_gates import BudgetContext, CostGateBlocked, CostGateMiddleware, CostReport


def test_tool_call_limit_blocks_before_second_execution() -> None:
    calls: list[str] = []

    def tool(_payload: dict[str, object]) -> dict[str, object]:
        calls.append("called")
        return {"ok": True}

    budget = BudgetContext(budget_id="limit", max_cost_micros=1000, max_tool_calls=1)
    report = CostReport(
        budget_id=budget.budget_id,
        max_cost_micros=budget.max_cost_micros,
        max_tool_calls=budget.max_tool_calls,
    )
    middleware = CostGateMiddleware(budget=budget, report=report, tools={"tool": tool})

    middleware.call(tool_name="tool", estimate_micros=100)
    with pytest.raises(CostGateBlocked, match="tool call limit exceeded"):
        middleware.call(tool_name="tool", estimate_micros=100)

    assert calls == ["called"]
    assert [event.status for event in report.events] == ["allowed", "blocked"]
    assert budget.counter.used == 1
