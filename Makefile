.PHONY: test lint compile demo validate

test:
	python3 -m pytest -o cache_dir=/tmp/agent-cost-gates-lab-pytest-cache

lint:
	python3 -m ruff check .

compile:
	python3 -m compileall src tests

demo:
	PYTHONPATH=src python3 -m cost_gates examples/cheap_task.json
	PYTHONPATH=src python3 -m cost_gates examples/expensive_task_blocked.json
	PYTHONPATH=src python3 -m cost_gates examples/fallback_triggered.json

validate: test lint compile demo

