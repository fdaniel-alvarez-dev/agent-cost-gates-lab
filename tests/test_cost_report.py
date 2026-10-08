from cost_gates import CostReport


def test_cost_report_totals_and_notice_do_not_claim_savings() -> None:
    report = CostReport(budget_id="report", max_cost_micros=1000, max_tool_calls=3)
    report.record(
        requested_tool="primary",
        executed_tool=None,
        status="blocked",
        estimate_micros=1200,
        charged_micros=0,
        reason="cost limit exceeded",
    )
    report.record(
        requested_tool="fallback",
        executed_tool="fallback",
        status="fallback",
        estimate_micros=200,
        charged_micros=200,
        reason="fallback_for=primary",
    )

    data = report.to_dict()
    rendered = report.render_text().lower()

    assert data["total_charged_micros"] == 200
    assert data["blocked_count"] == 1
    assert data["fallback_count"] == 1
    assert data["executed_tool_calls"] == 1
    assert "real-world" in data["notice"]
    assert "savings" not in rendered
