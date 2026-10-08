from __future__ import annotations

from dataclasses import dataclass

from cost_gates.budget import CostEstimate


@dataclass
class CostGateBlocked(Exception):
    """Raised when a proposed tool call is blocked before execution."""

    estimate: CostEstimate
    reason: str

    def __str__(self) -> str:
        return f"{self.estimate.tool_name} blocked: {self.reason}"
