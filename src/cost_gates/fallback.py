from __future__ import annotations

from dataclasses import dataclass

from cost_gates.exceptions import CostGateBlocked
from cost_gates.middleware import CostGateMiddleware, ToolPayload, ToolResult


@dataclass(frozen=True)
class FallbackPolicy:
    """Try a deterministic fallback tool when the primary tool is blocked."""

    fallback_tool: str
    fallback_estimate_micros: int

    def execute(
        self,
        *,
        middleware: CostGateMiddleware,
        primary_tool: str,
        primary_estimate_micros: int,
        payload: ToolPayload | None = None,
    ) -> ToolResult:
        try:
            return middleware.call(
                tool_name=primary_tool,
                estimate_micros=primary_estimate_micros,
                payload=payload,
            )
        except CostGateBlocked:
            return middleware.call(
                tool_name=self.fallback_tool,
                estimate_micros=self.fallback_estimate_micros,
                payload=payload,
                kind="fallback",
                reason=f"fallback_for={primary_tool}",
            )
