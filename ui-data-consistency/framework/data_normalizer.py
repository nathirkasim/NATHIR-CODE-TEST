from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Any


def normalize(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float, Decimal)):
        return value
    text = str(value).strip().lower()
    text = re.sub(r"\s+", " ", text)
    numeric = re.sub(r"[$€£¥,\s]", "", text)
    numeric = re.sub(r"(?:findings?|records?|items?)$", "", numeric).strip()
    if numeric.endswith("%"):
        numeric = numeric[:-1]
    try:
        number = Decimal(numeric)
        return int(number) if number == number.to_integral_value() else float(number)
    except InvalidOperation:
        return text


def normalized_context(context: dict[str, Any] | None) -> dict[str, Any]:
    return {key: normalize(value) for key, value in (context or {}).items()}
