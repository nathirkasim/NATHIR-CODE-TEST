from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from playwright.sync_api import Locator, Page

NUMBER_RE = re.compile(r"[-+]?\d[\d,]*(?:\.\d+)?%?")


@dataclass
class MetricSpec:
    name: str
    selector: str | None = None
    selector_type: str = "css"
    value_index: int = 0
    value_pattern: str | None = None
    attribute: str | None = None
    context: dict[str, str] = field(default_factory=dict)


@dataclass
class PageSpec:
    name: str
    url: str
    metrics: list[MetricSpec] = field(default_factory=list)
    login_path: str | None = None
    login_selectors: dict[str, str] = field(default_factory=dict)


def _locator(page: Page, metric: MetricSpec) -> Locator:
    if metric.selector_type == "text":
        return page.get_by_text(metric.selector or metric.name, exact=False)
    if metric.selector_type == "xpath":
        return page.locator(f"xpath={metric.selector or '//*'}")
    return page.locator(metric.selector or f"text={metric.name}")


def extract_text(page: Page, metric: MetricSpec) -> str | None:
    locator = _locator(page, metric)
    if locator.count() == 0:
        return None
    target = locator.nth(metric.value_index)
    if metric.attribute:
        return target.get_attribute(metric.attribute)
    return target.inner_text()


def extract_metric(page: Page, metric: MetricSpec) -> dict[str, Any]:
    text = extract_text(page, metric)
    if text is None:
        return {"name": metric.name, "raw": None, "value": None, "status": "missing", "context": metric.context}
    if metric.value_pattern:
        match = re.search(metric.value_pattern, text, re.IGNORECASE)
        raw = match.group(1) if match and match.groups() else (match.group(0) if match else text)
    else:
        matches = NUMBER_RE.findall(text)
        raw = matches[0] if matches else text.strip()
    return {"name": metric.name, "raw": raw, "value": raw, "status": "found", "source_text": text, "context": metric.context}


def extract_table(page: Page, selector: str = "table") -> list[dict[str, str]]:
    tables = page.locator(selector)
    if tables.count() == 0:
        return []
    table = tables.first
    headers = [cell.strip() for cell in table.locator("thead th").all_inner_texts()]
    rows: list[dict[str, str]] = []
    for row in table.locator("tbody tr").all():
        cells = [cell.strip() for cell in row.locator("th, td").all_inner_texts()]
        rows.append(dict(zip(headers or [str(i) for i in range(len(cells))], cells)))
    return rows


def extract_pagination_total(page: Page, selectors: list[str] | None = None) -> int | None:
    for selector in selectors or ["[aria-label*='pagination']", ".pagination", "body"]:
        text = page.locator(selector).first.inner_text() if page.locator(selector).count() else ""
        matches = re.findall(r"(?:of|total|/|from)\s+(\d[\d,]*)", text, re.IGNORECASE)
        if matches:
            return int(matches[-1].replace(",", ""))
    return None
