# Validation Report

Status: passed.

Environment:

- Python: 3.12.3
- Runtime dependencies: none
- Network/API usage: none
- Secrets required: none

Commands run:

```bash
python3 -m pytest -o cache_dir=/tmp/agent-cost-gates-lab-pytest-cache
python3 -m ruff check .
python3 -m compileall src tests
PYTHONPATH=src python3 -m cost_gates examples/cheap_task.json
PYTHONPATH=src python3 -m cost_gates examples/expensive_task_blocked.json
PYTHONPATH=src python3 -m cost_gates examples/fallback_triggered.json
```

Results:

- `pytest`: 5 passed.
- `ruff`: all checks passed.
- `compileall`: compiled `src` and `tests` successfully.
- `cheap_task.json`: 2 allowed calls, 0 blocked calls, 0 fallback calls, 1200 charged micros.
- `expensive_task_blocked.json`: 0 executed calls, 1 blocked call, 0 charged micros.
- `fallback_triggered.json`: 1 primary block, 1 fallback call, 300 charged micros.

Policy check:

- All examples run offline with deterministic local tools.
- Reports use task-provided estimates only.
- Reports do not claim real-world financial outcomes, discounts, billing accuracy, or production impact.
