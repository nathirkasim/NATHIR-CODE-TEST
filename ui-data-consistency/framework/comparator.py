from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

from .data_normalizer import normalize, normalized_context


@dataclass
class Mismatch:
    page: str
    metric: str
    expected: Any
    actual: Any
    difference: Any
    context: dict[str, Any]
    api_value: Any = None
    expected_source: str = ""
    actual_source: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def compare_values(expected: Any, actual: Any) -> tuple[bool, Any]:
    left, right = normalize(expected), normalize(actual)
    if left is None or right is None:
        return False, None
    if left == right:
        return True, 0
    try:
        return False, right - left
    except TypeError:
        return False, None


def compare_metric(page: str, metric: str, expected: Any, actual: Any, context: dict[str, Any] | None = None, **sources: str) -> Mismatch | None:
    matches, difference = compare_values(expected, actual)
    if matches:
        return None
    return Mismatch(page, metric, normalize(expected), normalize(actual), difference, normalized_context(context), **sources)


def same_context(left: dict[str, Any] | None, right: dict[str, Any] | None) -> bool:
    return normalized_context(left) == normalized_context(right)
