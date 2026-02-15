from __future__ import annotations

from collections import Counter
import re

from realitycheck_cli.ingest.pdf_parser import PageText


def _normalize_lines(text: str) -> list[str]:
    raw_lines = text.splitlines()
    lines = [re.sub(r"\s+", " ", line).strip() for line in raw_lines]
    return [line for line in lines if line]


def clean_pages(pages: list[PageText]) -> list[PageText]:
    if not pages:
        return []

    first_lines = Counter()
    last_lines = Counter()
    page_lines: list[tuple[int, list[str]]] = []
    for page in pages:
        lines = _normalize_lines(page.text)
        page_lines.append((page.page_number, lines))
        if lines:
            first_lines[lines[0].lower()] += 1
            last_lines[lines[-1].lower()] += 1

    threshold = max(2, int(len(pages) * 0.5))
    repeated_headers = {line for line, count in first_lines.items() if count >= threshold}
    repeated_footers = {line for line, count in last_lines.items() if count >= threshold}

    cleaned: list[PageText] = []
    for page_number, lines in page_lines:
        trimmed = list(lines)
        if trimmed and trimmed[0].lower() in repeated_headers:
            trimmed = trimmed[1:]
        if trimmed and trimmed[-1].lower() in repeated_footers:
            trimmed = trimmed[:-1]
        text = "\n".join(trimmed)
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        if text:
            cleaned.append(PageText(page_number=page_number, text=text))
    return cleaned

