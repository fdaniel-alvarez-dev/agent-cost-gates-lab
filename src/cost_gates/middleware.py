from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any, Literal

from cost_gates.budget import BudgetContext, CostEstimate
from cost_gates.exceptions import CostGateBlocked
from cost_gates.report import CostReport, EventStatus

ToolPayload = Mapping[str, Any]
ToolOutput = Mapping[str, Any]
ToolFunction = Callable[[ToolPayload], ToolOutput]
CallKind = Literal["primary", "fallback"]


@dataclass(frozen=True)
class ToolResult:
    tool_name: str
    status: EventStatus
    charged_micros: int
    output: ToolOutput


class CostGateMiddleware:
    """Pre-execution gate for deterministic tool-call estimates."""

    def __init__(
        self,
        *,
        budget: BudgetContext,
        report: CostReport,
        tools: Mapping[str, ToolFunction],
    ) -> None:
        self._budget = budget
        self._report = report
        self._tools = dict(tools)

    @property
    def budget(self) -> BudgetContext:
        return self._budget

    @property
    def report(self) -> CostReport:
        return self._report

    def call(
        self,
        *,
        tool_name: str,
        estimate_micros: int,
        payload: ToolPayload | None = None,
        kind: CallKind = "primary",
        reason: str | None = None,
    ) -> ToolResult:
        estimate = CostEstimate(tool_name=tool_name, cost_micros=estimate_micros)
        blocking_reason = self._budget.check(estimate)
        status: EventStatus = "fallback" if kind == "fallback" else "allowed"

        if blocking_reason is not None:
            self._report.record(
                requested_tool=tool_name,
                executed_tool=None,
                status="blocked",
                estimate_micros=estimate.cost_micros,
                charged_micros=0,
                reason=blocking_reason,
            )
            raise CostGateBlocked(estimate=estimate, reason=blocking_reason)

        tool = self._tools.get(tool_name)
        if tool is None:
            raise KeyError(f"unknown tool: {tool_name}")

        self._budget.charge(estimate)
        output = tool(payload or {})
        self._report.record(
            requested_tool=tool_name,
            executed_tool=tool_name,
            status=status,
            estimate_micros=estimate.cost_micros,
            charged_micros=estimate.cost_micros,
            reason=reason,
        )
        return ToolResult(
            tool_name=tool_name,
            status=status,
            charged_micros=estimate.cost_micros,
            output=output,
        )
