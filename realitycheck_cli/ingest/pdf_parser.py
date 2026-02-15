from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import pdfplumber


@dataclass(frozen=True)
class PageText:
    page_number: int
    text: str


def parse_pdf(path: Path) -> list[PageText]:
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")
    pages: list[PageText] = []
    with pdfplumber.open(path) as pdf:
        for idx, page in enumerate(pdf.pages, start=1):
            extracted = page.extract_text() or ""
            if extracted.strip():
                pages.append(PageText(page_number=idx, text=extracted))
    if not pages:
        raise ValueError(f"No extractable text was found in PDF: {path}")
    return pages

