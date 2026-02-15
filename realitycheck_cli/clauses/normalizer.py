from __future__ import annotations

import re
from difflib import SequenceMatcher


def normalize_clause_text(text: str) -> str:
    normalized = text.lower()
    normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def canonical_title(title: str) -> str:
    return normalize_clause_text(title)


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize_clause_text(a), normalize_clause_text(b)).ratio()

