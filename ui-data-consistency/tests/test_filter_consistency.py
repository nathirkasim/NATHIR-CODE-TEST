from __future__ import annotations

import pytest

from framework.comparator import compare_metric


def test_filter_count_vs_displayed_result_count(runner, pages):
    mismatch = runner.compare_pages(pages["Overview"], pages["Repository Findings"], pages["Overview"].metrics[0], pages["Repository Findings"].metrics[0])
    if mismatch:
        pytest.fail(f"Filter/result mismatch: expected {mismatch.expected}, actual {mismatch.actual}")


def test_context_prevents_false_positive():
    mismatch = compare_metric("Repository", "SAST", 100, 20, {"repository": "selected-repository", "scope": "selected"})
    assert mismatch is not None
    assert mismatch.context["scope"] == "selected"
