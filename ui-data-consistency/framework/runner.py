from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from playwright.sync_api import Page

from .ai_analyzer import AiAnalyzer
from .api_capture import ApiCapture
from .browser import BrowserSession, screenshot
from .bug_reporter import BugReporter
from .comparator import Mismatch, compare_metric
from .ui_extractor import MetricSpec, PageSpec, extract_metric

LOGGER = logging.getLogger(__name__)


class ConsistencyRunner:
    def __init__(self, root: Path, session: BrowserSession) -> None:
        self.root = root
        self.session = session
        self.capture = ApiCapture(root / "reports")
        self.analyzer = AiAnalyzer()
        self.reporter = BugReporter(root)
        self.results: list[dict[str, Any]] = []
        self._login_done = False

    def open_page(self, page: Page, spec: PageSpec) -> dict[str, dict[str, Any]]:
        if not self._login_done:
            self.session.login(page, spec.login_path, spec.login_selectors)
            self._login_done = True
        self.capture.attach(page)
        page.goto(self.session.url(spec.url), wait_until="domcontentloaded")
        try:
            page.wait_for_load_state("networkidle")
        except Exception:
            LOGGER.warning("Network did not become idle for %s; extracting visible state.", spec.name)
        return {metric.name: extract_metric(page, metric) for metric in spec.metrics}

    def compare_pages(self, left: PageSpec, right: PageSpec, left_metric: MetricSpec, right_metric: MetricSpec | None = None) -> Mismatch | None:
        right_metric = right_metric or left_metric
        with self.session.page() as left_page:
            left_values = self.open_page(left_page, left)
            with self.session.page() as right_page:
                right_values = self.open_page(right_page, right)
                expected = left_values.get(left_metric.name, {}).get("value")
                actual = right_values.get(right_metric.name, {}).get("value")
                mismatch = compare_metric(left.name, left_metric.name, expected, actual, context={**left_metric.context, **right_metric.context}, expected_source=left.name, actual_source=right.name, api_value=self.capture.find_json_value(left_metric.name))
                if mismatch:
                    paths = [
                        screenshot(left_page, self.root / "screenshots" / f"{_safe(left.name)}_{_safe(left_metric.name)}_expected.png"),
                        screenshot(right_page, self.root / "screenshots" / f"{_safe(right.name)}_{_safe(right_metric.name)}_actual.png"),
                    ]
                    ai = self.analyzer.analyze(mismatch.as_dict())
                    report = self.reporter.write(mismatch, ai, paths)
                    self.results.append(report)
                return mismatch

    def finalize(self) -> None:
        self.reporter.write_reports(self.results)


def _safe(value: str) -> str:
    return "_".join(value.lower().split()).replace("/", "-")
