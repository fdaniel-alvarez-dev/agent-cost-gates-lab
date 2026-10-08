import pytest

from cost_gates import BudgetContext, CostEstimate


def test_budget_context_charges_allowed_estimate() -> None:
    budget = BudgetContext(
        budget_id="unit",
        max_cost_micros=1000,
        max_tool_calls=2,
    )

    budget.charge(CostEstimate(tool_name="local_lookup", cost_micros=400))

    assert budget.spent_micros == 400
    assert budget.remaining_cost_micros == 600
    assert budget.counter.used == 1


def test_budget_context_rejects_over_budget_without_mutating_state() -> None:
    budget = BudgetContext(
        budget_id="unit",
        max_cost_micros=1000,
        max_tool_calls=2,
    )
    estimate = CostEstimate(tool_name="expensive", cost_micros=1200)

    assert budget.can_afford(estimate) is False
    with pytest.raises(ValueError, match="cost limit exceeded"):
        budget.charge(estimate)

    assert budget.spent_micros == 0
    assert budget.counter.used == 0
