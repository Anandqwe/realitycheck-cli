from __future__ import annotations

import re

from realitycheck_cli.analysis.schemas import Clause
from realitycheck_cli.ingest.pdf_parser import PageText

_HEADING_RE = re.compile(r"^\s*(\d+(?:\.\d+)*)[\).:-]?\s+(.+)$")
_ALL_CAPS_HEADING_RE = re.compile(r"^[A-Z][A-Z\s/&-]{3,80}$")


def _is_heading(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if _HEADING_RE.match(stripped):
        return True
    return bool(_ALL_CAPS_HEADING_RE.match(stripped) and len(stripped.split()) <= 12)


def _heading_title(line: str) -> str:
    match = _HEADING_RE.match(line.strip())
    if match:
        return match.group(2).strip().title()
    return line.strip().title()


def split_into_clauses(contract_id: str, pages: list[PageText]) -> list[Clause]:
    if not pages:
        return []

    clauses: list[Clause] = []
    buffer: list[str] = []
    active_title = "Preamble"
    active_page = pages[0].page_number

    def flush_clause() -> None:
        if not buffer:
            return
        text = "\n".join(buffer).strip()
        if not text:
            return
        clause_id = f"C-{len(clauses) + 1:03d}"
        clauses.append(
            Clause(
                contract_id=contract_id,
                clause_id=clause_id,
                title=active_title,
                page=active_page,
                text=text,
            )
        )

    for page in pages:
        for raw_line in page.text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if _is_heading(line):
                flush_clause()
                buffer.clear()
                active_title = _heading_title(line)
                active_page = page.page_number
                continue
            buffer.append(line)

    flush_clause()

    if not clauses:
        combined = "\n".join(page.text for page in pages).strip()
        if combined:
            clauses.append(
                Clause(
                    contract_id=contract_id,
                    clause_id="C-001",
                    title="Full Agreement",
                    page=pages[0].page_number,
                    text=combined,
                )
            )
    return clauses

