from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

EventStatus = Literal["allowed", "blocked", "fallback"]

NO_FAKE_SAVINGS_NOTICE = (
    "Report uses deterministic task-provided estimates only; it does not claim "
    "real-world financial outcomes, discounts, or billing accuracy."
)


@dataclass(frozen=True)
class ToolEvent:
    sequence: int
    requested_tool: str
    executed_tool: str | None
    status: EventStatus
    estimate_micros: int
    charged_micros: int
    reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "requested_tool": self.requested_tool,
            "executed_tool": self.executed_tool,
            "status": self.status,
            "estimate_micros": self.estimate_micros,
            "charged_micros": self.charged_micros,
            "reason": self.reason,
        }


@dataclass
class CostReport:
    budget_id: str
    max_cost_micros: int
    max_tool_calls: int
    events: list[ToolEvent] = field(default_factory=list)

    def record(
        self,
        *,
        requested_tool: str,
        executed_tool: str | None,
        status: EventStatus,
        estimate_micros: int,
        charged_micros: int,
        reason: str | None = None,
    ) -> ToolEvent:
        event = ToolEvent(
            sequence=len(self.events) + 1,
            requested_tool=requested_tool,
            executed_tool=executed_tool,
            status=status,
            estimate_micros=estimate_micros,
            charged_micros=charged_micros,
            reason=reason,
        )
        self.events.append(event)
        return event

    @property
    def total_charged_micros(self) -> int:
        return sum(event.charged_micros for event in self.events)

    @property
    def executed_tool_calls(self) -> int:
        return sum(1 for event in self.events if event.status in {"allowed", "fallback"})

    @property
    def blocked_count(self) -> int:
        return sum(1 for event in self.events if event.status == "blocked")

    @property
    def fallback_count(self) -> int:
        return sum(1 for event in self.events if event.status == "fallback")

    def to_dict(self) -> dict[str, Any]:
        return {
            "budget_id": self.budget_id,
            "max_cost_micros": self.max_cost_micros,
            "max_tool_calls": self.max_tool_calls,
            "total_charged_micros": self.total_charged_micros,
            "executed_tool_calls": self.executed_tool_calls,
            "blocked_count": self.blocked_count,
            "fallback_count": self.fallback_count,
            "notice": NO_FAKE_SAVINGS_NOTICE,
            "events": [event.to_dict() for event in self.events],
        }

    def render_text(self) -> str:
        lines = [
            f"Budget: {self.budget_id}",
            f"Max deterministic cost: {self.max_cost_micros} micros",
            f"Max tool calls: {self.max_tool_calls}",
            f"Total charged estimate: {self.total_charged_micros} micros",
            f"Executed tool calls: {self.executed_tool_calls}",
            f"Blocked calls: {self.blocked_count}",
            f"Fallback calls: {self.fallback_count}",
            "Events:",
        ]
        for event in self.events:
            executed = event.executed_tool or "-"
            reason = f" reason={event.reason}" if event.reason else ""
            lines.append(
                f"  {event.sequence}. {event.status} requested={event.requested_tool} "
                f"executed={executed} estimate={event.estimate_micros} "
                f"charged={event.charged_micros}{reason}"
            )
        lines.append(f"Notice: {NO_FAKE_SAVINGS_NOTICE}")
        return "\n".join(lines)
