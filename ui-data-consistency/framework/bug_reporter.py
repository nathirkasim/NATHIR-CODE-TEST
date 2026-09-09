from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .comparator import Mismatch


class BugReporter:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.report_dir = root / "reports"
        self.bug_dir = self.report_dir / "bug_reports"
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.bug_dir.mkdir(parents=True, exist_ok=True)

    def write(self, mismatch: Mismatch, ai: dict[str, Any], screenshots: list[str] | None = None) -> dict[str, Any]:
        data = {"mismatch": mismatch.as_dict(), "ai": ai, "screenshots": screenshots or [], "created_at": datetime.now(timezone.utc).isoformat()}
        title = f"{mismatch.metric} value mismatch"
        context = ", ".join(f"{key}={value}" for key, value in mismatch.context.items()) or "the same configured context"
        text = f"Bug: {title} — {mismatch.expected_source or 'Expected page'} shows {mismatch.expected}, while {mismatch.actual_source or 'actual page'} shows {mismatch.actual} for {context}. The application should display consistent values when the same context and filters are applied."
        data["formatted_report"] = f"Bug: {title}\n\nSteps to Reproduce:\n1. Navigate to {mismatch.expected_source or 'the expected page'}.\n2. Apply context: {context}.\n3. Navigate to {mismatch.actual_source or 'the actual page'} and compare {mismatch.metric}.\n\nActual Result:\n{mismatch.actual}\n\nExpected Result:\n{mismatch.expected}\n\nParagraph:\n{text}"
        path = self.bug_dir / f"{_safe_name(title)}.json"
        path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        return data

    def write_reports(self, mismatches: list[dict[str, Any]]) -> None:
        (self.report_dir / "mismatches.json").write_text(json.dumps(mismatches, indent=2, default=str), encoding="utf-8")
        (self.report_dir / "consistency_report.json").write_text(json.dumps(mismatches, indent=2, default=str), encoding="utf-8")
        rows = "".join(self._row(item) for item in mismatches)
        document = f"<html><head><meta charset='utf-8'><title>Consistency report</title></head><body><h1>Consistency report</h1><table border='1'><tr><th>Page</th><th>Metric</th><th>Expected</th><th>Actual</th><th>Difference</th><th>Context</th><th>API</th><th>AI</th><th>Confidence</th><th>Screenshots</th></tr>{rows}</table></body></html>"
        (self.report_dir / "consistency_report.html").write_text(document, encoding="utf-8")

    @staticmethod
    def _row(item: dict[str, Any]) -> str:
        mismatch = item.get("mismatch", item)
        ai = item.get("ai", {})
        links = " ".join(f"<a href='../screenshots/{html.escape(Path(path).name)}'>screenshot</a>" for path in item.get("screenshots", []))
        cells = [mismatch.get(key, "") for key in ("page", "metric", "expected", "actual", "difference", "context", "api_value")]
        cells += [ai.get("is_bug", ""), ai.get("confidence", ""), links]
        return "<tr>" + "".join(f"<td>{html.escape(str(cell))}</td>" for cell in cells) + "</tr>"


def _safe_name(value: str) -> str:
    return "-".join(value.lower().split()).replace("/", "-")
