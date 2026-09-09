from __future__ import annotations

import json
import logging
import os
from typing import Any

LOGGER = logging.getLogger(__name__)

SYSTEM_PROMPT = """You analyze UI data mismatches. Return JSON only with keys is_bug (boolean), confidence (0-1), reason (string), severity (low|medium|high). Consider context before calling a difference a bug."""


class AiAnalyzer:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def analyze(self, comparison: dict[str, Any]) -> dict[str, Any]:
        if not self.api_key:
            return {"is_bug": False, "confidence": 0.0, "reason": "AI analysis disabled: OPENAI_API_KEY is not configured.", "severity": "low"}
        try:
            from openai import OpenAI
            response = OpenAI(api_key=self.api_key).chat.completions.create(
                model=self.model,
                temperature=0,
                response_format={"type": "json_object"},
                messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": json.dumps(comparison, default=str)}],
            )
            return json.loads(response.choices[0].message.content or "{}")
        except Exception as error:
            LOGGER.exception("AI analysis failed")
            return {"is_bug": False, "confidence": 0.0, "reason": f"AI analysis unavailable: {error}", "severity": "low"}
