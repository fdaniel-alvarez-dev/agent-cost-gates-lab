from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CostEstimate:
    """A deterministic, caller-supplied estimate for one proposed tool action."""

    tool_name: str
    cost_micros: int
    tool_calls: int = 1

    def __post_init__(self) -> None:
        if not self.tool_name:
            raise ValueError("tool_name must not be empty")
        if self.cost_micros < 0:
            raise ValueError("cost_micros must be non-negative")
        if self.tool_calls < 1:
            raise ValueError("tool_calls must be at least 1")


@dataclass
class ToolCallCounter:
    """Hard counter for attempted tool executions that pass the gate."""

    limit: int
    used: int = 0

    def __post_init__(self) -> None:
        if self.limit < 0:
            raise ValueError("limit must be non-negative")
        if self.used < 0:
            raise ValueError("used must be non-negative")
        if self.used > self.limit:
            raise ValueError("used must not exceed limit")

    @property
    def remaining(self) -> int:
        return self.limit - self.used

    def can_use(self, calls: int = 1) -> bool:
        if calls < 1:
            raise ValueError("calls must be at least 1")
        return self.used + calls <= self.limit

    def increment(self, calls: int = 1) -> None:
        if not self.can_use(calls):
            raise ValueError("tool call limit exceeded")
        self.used += calls


@dataclass
class BudgetContext:
    """Mutable budget state shared by an agent run."""

    budget_id: str
    max_cost_micros: int
    max_tool_calls: int
    spent_micros: int = 0
    counter: ToolCallCounter = field(init=False)

    def __post_init__(self) -> None:
        if not self.budget_id:
            raise ValueError("budget_id must not be empty")
        if self.max_cost_micros < 0:
            raise ValueError("max_cost_micros must be non-negative")
        if self.max_tool_calls < 0:
            raise ValueError("max_tool_calls must be non-negative")
        if self.spent_micros < 0:
            raise ValueError("spent_micros must be non-negative")
        if self.spent_micros > self.max_cost_micros:
            raise ValueError("spent_micros must not exceed max_cost_micros")
        self.counter = ToolCallCounter(limit=self.max_tool_calls)

    @property
    def remaining_cost_micros(self) -> int:
        return self.max_cost_micros - self.spent_micros

    def check(self, estimate: CostEstimate) -> str | None:
        """Return a blocking reason, or None when the estimate can be charged."""

        if self.spent_micros + estimate.cost_micros > self.max_cost_micros:
            return (
                f"cost limit exceeded: requested={estimate.cost_micros}, "
                f"remaining={self.remaining_cost_micros}"
            )
        if not self.counter.can_use(estimate.tool_calls):
            return (
                f"tool call limit exceeded: requested={estimate.tool_calls}, "
                f"remaining={self.counter.remaining}"
            )
        return None

    def can_afford(self, estimate: CostEstimate) -> bool:
        return self.check(estimate) is None

    def charge(self, estimate: CostEstimate) -> None:
        reason = self.check(estimate)
        if reason is not None:
            raise ValueError(reason)
        self.spent_micros += estimate.cost_micros
        self.counter.increment(estimate.tool_calls)
