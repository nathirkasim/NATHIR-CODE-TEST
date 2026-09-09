from __future__ import annotations

import pytest

from framework.comparator import compare_metric


def test_dashboard_count_vs_detailed_findings_count(runner, pages):
    left = pages["Overview"]
    right = pages["Repository Findings"]
    mismatch = runner.compare_pages(left, right, left.metrics[0], right.metrics[0])
    if mismatch:
        pytest.fail(f"{mismatch.metric}: expected {mismatch.expected}, actual {mismatch.actual}")


def test_summary_card_vs_chart_total_deterministic():
    mismatch = compare_metric("Overview", "SAST", "1,583", "1,583", {"repository": "repo-a", "branch": "main"})
    assert mismatch is None
