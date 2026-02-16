from __future__ import annotations

import json
from typing import Any

import google.generativeai as genai

from realitycheck_cli.analysis.schemas import Clause
from realitycheck_cli.config.settings import Settings

_SYSTEM_PROMPT = """You are a legal contract clause analyzer.
Return JSON only. No markdown.

Required JSON keys:
- category: one of NON_COMPETE, IP_TRANSFER, LIABILITY, TERMINATION, FINANCIAL_RISK, PRIVACY, NEUTRAL
- category_confidence: float 0..1
- risk_level: LOW, MEDIUM, HIGH, or CRITICAL
- risk_score: integer 0..100
- benefits_party: CLIENT, VENDOR, MUTUAL, or UNKNOWN
- explanation: short rationale
- signals: array of objects with keys {type, label, severity, evidence}
  where type is one of VAGUE_LANGUAGE, MISSING_PROTECTION, ONE_SIDED_RIGHT, LIABILITY_EXPANSION
  and severity is LOW, MEDIUM, HIGH
"""


def _extract_text(response: Any) -> str | None:
    text = getattr(response, "text", None)
    if isinstance(text, str) and text.strip():
        return text
    candidates = getattr(response, "candidates", None)
    if not candidates:
        return None
    for candidate in candidates:
        content = getattr(candidate, "content", None)
        parts = getattr(content, "parts", None) if content else None
        if not parts:
            continue
        for part in parts:
            part_text = getattr(part, "text", None)
            if isinstance(part_text, str) and part_text.strip():
                return part_text
    return None


class LLMClient:
    def __init__(self, settings: Settings) -> None:
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required when LLM classification is enabled.")
        genai.configure(api_key=settings.gemini_api_key)
        self._timeout_seconds = settings.llm_timeout_seconds
        self._model = genai.GenerativeModel(
            model_name=settings.gemini_model,
            system_instruction=_SYSTEM_PROMPT,
        )

    def classify_clause(self, clause: Clause, heuristic_snapshot: dict[str, Any]) -> dict[str, Any]:
        user_prompt = (
            "Classify this clause.\n\n"
            f"Clause:\n{clause.model_dump_json(indent=2)}\n\n"
            f"Heuristic baseline (use as reference, but improve if needed):\n"
            f"{json.dumps(heuristic_snapshot, indent=2)}"
        )
        response = self._model.generate_content(
            user_prompt,
            generation_config={
                "temperature": 0.1,
                "response_mime_type": "application/json",
            },
            request_options={"timeout": self._timeout_seconds},
        )
        content = _extract_text(response)
        if content is None:
            raise ValueError("Gemini returned empty content.")
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError("Gemini response was not valid JSON.") from exc
        if not isinstance(parsed, dict):
            raise ValueError("Gemini response JSON must be an object.")
        return parsed
