from __future__ import annotations

import pytest

from framework.comparator import compare_metric


def test_repository_overview_vs_repository_details(runner, pages):
    mismatch = runner.compare_pages(pages["Overview"], pages["Repository Findings"], pages["Overview"].metrics[0], pages["Repository Findings"].metrics[0])
    if mismatch:
        pytest.fail(f"Repository mismatch: expected {mismatch.expected}, actual {mismatch.actual}")


def test_ui_value_vs_api_value_is_normalized():
    mismatch = compare_metric("Overview", "SAST", "1,583 findings", "1583", {"branch": "main"})
    assert mismatch is None
