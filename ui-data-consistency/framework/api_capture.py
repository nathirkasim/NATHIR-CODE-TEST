from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from playwright.sync_api import Page, Response

LOGGER = logging.getLogger(__name__)


class ApiCapture:
    def __init__(self, report_dir: Path) -> None:
        self.report_dir = report_dir
        self.api_dir = report_dir / "api"
        self.api_dir.mkdir(parents=True, exist_ok=True)
        self.records: list[dict[str, Any]] = []

    def attach(self, page: Page) -> None:
        page.on("response", self._handle_response)

    def _handle_response(self, response: Response) -> None:
        if response.request.resource_type not in {"xhr", "fetch"}:
            return
        record: dict[str, Any] = {
            "url": response.url,
            "method": response.request.method,
            "status": response.status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "json": None,
        }
        try:
            record["json"] = response.json()
            path = self.api_dir / f"response_{len(self.records) + 1:04d}.json"
            path.write_text(json.dumps(record, indent=2, default=str), encoding="utf-8")
            record["saved_to"] = str(path)
        except Exception:
            LOGGER.debug("Response was not JSON: %s", response.url)
        self.records.append(record)

    def find_json_value(self, key: str, url_contains: str | None = None) -> Any:
        for record in reversed(self.records):
            if url_contains and url_contains not in record["url"]:
                continue
            value = _find_key(record.get("json"), key)
            if value is not None:
                return value
        return None


def _find_key(value: Any, key: str) -> Any:
    if isinstance(value, dict):
        if key in value:
            return value[key]
        for child in value.values():
            result = _find_key(child, key)
            if result is not None:
                return result
    elif isinstance(value, list):
        for child in value:
            result = _find_key(child, key)
            if result is not None:
                return result
    return None
