from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str | None
    gemini_model: str
    high_risk_threshold: int
    llm_timeout_seconds: int

    @classmethod
    def from_env(cls) -> "Settings":
        threshold_raw = os.getenv("REALITYCHECK_HIGH_RISK_THRESHOLD", "70")
        timeout_raw = os.getenv("REALITYCHECK_LLM_TIMEOUT", "45")
        try:
            threshold = int(threshold_raw)
        except ValueError as exc:
            raise ValueError(
                "REALITYCHECK_HIGH_RISK_THRESHOLD must be an integer."
            ) from exc
        try:
            timeout = int(timeout_raw)
        except ValueError as exc:
            raise ValueError("REALITYCHECK_LLM_TIMEOUT must be an integer.") from exc
        return cls(
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            gemini_model=os.getenv("REALITYCHECK_GEMINI_MODEL", "gemini-3-flash-preview"),
            high_risk_threshold=max(1, min(100, threshold)),
            llm_timeout_seconds=max(5, timeout),
        )

