from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from cost_gates.budget import BudgetContext
from cost_gates.exceptions import CostGateBlocked
from cost_gates.fallback import FallbackPolicy
from cost_gates.middleware import CostGateMiddleware
from cost_gates.report import CostReport


def local_lookup(payload: dict[str, Any]) -> dict[str, Any]:
    query = str(payload.get("query", "")).strip()
    return {"result": f"local_lookup:{query or 'empty'}"}


def local_summary(payload: dict[str, Any]) -> dict[str, Any]:
    text = str(payload.get("text", ""))
    max_chars = int(payload.get("max_chars", 80))
    return {"summary": text[:max_chars]}


def deterministic_expensive_model(payload: dict[str, Any]) -> dict[str, Any]:
    prompt = str(payload.get("prompt", ""))
    return {"result": f"deterministic_model:{len(prompt)}"}


def local_fallback_summary(payload: dict[str, Any]) -> dict[str, Any]:
    text = str(payload.get("text") or payload.get("prompt") or "")
    return {"summary": f"fallback:{text[:48]}"}


LOCAL_TOOLS = {
    "local_lookup": local_lookup,
    "local_summary": local_summary,
    "deterministic_expensive_model": deterministic_expensive_model,
    "local_fallback_summary": local_fallback_summary,
}


def load_task(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_fallback_policy(task: dict[str, Any]) -> FallbackPolicy | None:
    fallback_config = task.get("fallback_policy")
    if fallback_config is None:
        return None
    return FallbackPolicy(
        fallback_tool=str(fallback_config["fallback_tool"]),
        fallback_estimate_micros=int(fallback_config["fallback_estimate_micros"]),
    )


def run_task(task: dict[str, Any]) -> CostReport:
    budget_config = task["budget"]
    budget = BudgetContext(
        budget_id=str(task["task_id"]),
        max_cost_micros=int(budget_config["max_cost_micros"]),
        max_tool_calls=int(budget_config["max_tool_calls"]),
    )
    report = CostReport(
        budget_id=budget.budget_id,
        max_cost_micros=budget.max_cost_micros,
        max_tool_calls=budget.max_tool_calls,
    )
    middleware = CostGateMiddleware(budget=budget, report=report, tools=LOCAL_TOOLS)
    fallback_policy = build_fallback_policy(task)

    for step in task.get("steps", []):
        tool_name = str(step["tool"])
        estimate_micros = int(step["estimate_micros"])
        payload = step.get("input", {})
        if fallback_policy is not None and step.get("fallback_enabled", True):
            try:
                fallback_policy.execute(
                    middleware=middleware,
                    primary_tool=tool_name,
                    primary_estimate_micros=estimate_micros,
                    payload=payload,
                )
            except CostGateBlocked:
                continue
        else:
            try:
                middleware.call(
                    tool_name=tool_name,
                    estimate_micros=estimate_micros,
                    payload=payload,
                )
            except CostGateBlocked:
                continue
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run deterministic agent cost-gate examples.")
    parser.add_argument("task_file", type=Path, help="Path to a JSON task file.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable report JSON.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = run_task(load_task(args.task_file))
    if args.json:
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    else:
        print(report.render_text())
    return 0
