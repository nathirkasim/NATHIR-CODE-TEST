from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .ui_extractor import MetricSpec, PageSpec


def load_config(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        return yaml.safe_load(stream) or {}


def page_specs(config: dict[str, Any]) -> dict[str, PageSpec]:
    login = config.get("login", {})
    specs: dict[str, PageSpec] = {}
    for item in config.get("pages", []):
        metrics = [MetricSpec(**metric) for metric in item.get("metrics", [])]
        specs[item["name"]] = PageSpec(item["name"], item["url"], metrics, login.get("path"), login.get("selectors", {}))
    return specs
