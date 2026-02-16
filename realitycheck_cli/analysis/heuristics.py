from __future__ import annotations

import re

from realitycheck_cli.analysis.schemas import (
    BenefitsParty,
    Clause,
    ClauseCategory,
    ClauseSignal,
    RiskLevel,
    Severity,
    SignalType,
)

_CATEGORY_PATTERNS: dict[ClauseCategory, tuple[str, ...]] = {
    ClauseCategory.NON_COMPETE: (
        r"\bnon[- ]?compete\b",
        r"\bnon[- ]?solicit(?:ation)?\b",
        r"\brestrict(?:ion|ed)?\s+from\s+working\b",
    ),
    ClauseCategory.IP_TRANSFER: (
        r"\bintellectual property\b",
        r"\bwork product\b",
        r"\bassign(?:ment|ed|s)?\b",
        r"\bownership rights\b",
    ),
    ClauseCategory.LIABILITY: (
        r"\bliabilit(?:y|ies)\b",
        r"\bindemnif(?:y|ication)\b",
        r"\bconsequential damages\b",
        r"\blimit(?:ation)? of liability\b",
    ),
    ClauseCategory.TERMINATION: (
        r"\bterminat(?:e|ion)\b",
        r"\bcure period\b",
        r"\bmaterial breach\b",
        r"\bnotice period\b",
    ),
    ClauseCategory.FINANCIAL_RISK: (
        r"\bpayment\b",
        r"\binvoice\b",
        r"\blate fee\b",
        r"\bfee(?:s)?\b",
        r"\bnet\s*\d+\b",
    ),
    ClauseCategory.PRIVACY: (
        r"\bconfidential(?:ity)?\b",
        r"\bpersonal data\b",
        r"\bprivacy\b",
        r"\bdata protection\b",
        r"\bbreach notification\b",
    ),
    ClauseCategory.NEUTRAL: (),
}

_VAGUE_PATTERNS: tuple[tuple[str, str, Severity], ...] = (
    (r"\bsole\s+discretion\b", "sole discretion", Severity.HIGH),
    (r"\bwithout\s+notice\b", "without notice", Severity.HIGH),
    (r"\bas\s+deemed\s+necessary\b", "as deemed necessary", Severity.MEDIUM),
    (
        r"\bat\s+any\s+time\s+for\s+any\s+reason\b",
        "at any time for any reason",
        Severity.HIGH,
    ),
)

_ONE_SIDED_PATTERNS: tuple[tuple[str, str, Severity], ...] = (
    (
        r"\bmay\s+terminate\b.{0,60}\bwithout\s+notice\b",
        "termination without notice",
        Severity.HIGH,
    ),
    (r"\bunilateral(?:ly)?\b", "unilateral rights", Severity.HIGH),
    (r"\bfor any reason\b", "for any reason", Severity.MEDIUM),
)

_LIABILITY_EXPANSION_PATTERNS: tuple[tuple[str, str, Severity], ...] = (
    (r"\bunlimited liability\b", "unlimited liability", Severity.HIGH),
    (r"\bliability shall not be limited\b", "liability not limited", Severity.HIGH),
    (r"\ball damages\b", "all damages", Severity.MEDIUM),
    (r"\bconsequential damages\b", "consequential damages exposure", Severity.MEDIUM),
)

_CATEGORY_BASE_RISK: dict[ClauseCategory, int] = {
    ClauseCategory.NON_COMPETE: 60,
    ClauseCategory.IP_TRANSFER: 57,
    ClauseCategory.LIABILITY: 62,
    ClauseCategory.TERMINATION: 55,
    ClauseCategory.FINANCIAL_RISK: 58,
    ClauseCategory.PRIVACY: 52,
    ClauseCategory.NEUTRAL: 35,
}

_SEVERITY_POINTS = {
    Severity.LOW: 4,
    Severity.MEDIUM: 8,
    Severity.HIGH: 14,
}


def detect_category(text: str) -> tuple[ClauseCategory, float]:
    lowered = text.lower()
    best_category = ClauseCategory.NEUTRAL
    best_score = 0
    for category, patterns in _CATEGORY_PATTERNS.items():
        score = sum(1 for pattern in patterns if re.search(pattern, lowered))
        if score > best_score:
            best_score = score
            best_category = category
    if best_score == 0:
        return ClauseCategory.NEUTRAL, 0.35
    confidence = min(0.95, 0.45 + (best_score * 0.12))
    return best_category, confidence


def _signal_from_match(
    signal_type: SignalType,
    label: str,
    severity: Severity,
    text: str,
    match: re.Match[str],
) -> ClauseSignal:
    start = max(0, match.start() - 30)
    end = min(len(text), match.end() + 30)
    evidence = text[start:end].strip()
    return ClauseSignal(
        type=signal_type,
        label=label,
        severity=severity,
        evidence=evidence,
    )


def detect_signals(text: str) -> list[ClauseSignal]:
    lowered = text.lower()
    signals: list[ClauseSignal] = []

    for pattern, label, severity in _VAGUE_PATTERNS:
        match = re.search(pattern, lowered, flags=re.DOTALL)
        if match:
            signals.append(
                _signal_from_match(SignalType.VAGUE_LANGUAGE, label, severity, text, match)
            )

    for pattern, label, severity in _ONE_SIDED_PATTERNS:
        match = re.search(pattern, lowered, flags=re.DOTALL)
        if match:
            signals.append(
                _signal_from_match(SignalType.ONE_SIDED_RIGHT, label, severity, text, match)
            )

    for pattern, label, severity in _LIABILITY_EXPANSION_PATTERNS:
        match = re.search(pattern, lowered, flags=re.DOTALL)
        if match:
            signals.append(
                _signal_from_match(
                    SignalType.LIABILITY_EXPANSION, label, severity, text, match
                )
            )

    return signals


def detect_benefits_party(text: str) -> BenefitsParty:
    lowered = text.lower()
    if any(marker in lowered for marker in ("mutual", "both parties", "each party")):
        return BenefitsParty.MUTUAL

    client_has_right = bool(re.search(r"\b(client|company|customer)\s+may\b", lowered))
    vendor_has_right = bool(re.search(r"\b(vendor|provider|contractor)\s+may\b", lowered))
    if client_has_right and not vendor_has_right:
        return BenefitsParty.CLIENT
    if vendor_has_right and not client_has_right:
        return BenefitsParty.VENDOR
    if client_has_right and vendor_has_right:
        return BenefitsParty.MUTUAL
    return BenefitsParty.UNKNOWN


def estimate_risk_score(category: ClauseCategory, signals: list[ClauseSignal]) -> int:
    base = _CATEGORY_BASE_RISK[category]
    signal_points = sum(_SEVERITY_POINTS[signal.severity] for signal in signals)
    score = base + signal_points
    return max(1, min(100, score))


def risk_level_from_score(score: int) -> RiskLevel:
    if score >= 85:
        return RiskLevel.CRITICAL
    if score >= 70:
        return RiskLevel.HIGH
    if score >= 45:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


def detect_missing_protections(clauses: list[Clause]) -> list[str]:
    text = " ".join(clause.text.lower() for clause in clauses)
    missing: list[str] = []

    payment_pattern = r"(payment|invoice).{0,40}(due|within|days|net\s*\d+)"
    if not re.search(payment_pattern, text, flags=re.DOTALL):
        missing.append("payment_timeline")

    termination_notice_pattern = (
        r"((terminate|termination).{0,80}(written\s+notice|notice\s+period|days?\s+notice|notice\s+of|(\d+|\w+)\s+days))"
        r"|((written\s+notice|notice\s+period|days?\s+notice|notice\s+of|(\d+|\w+)\s+days).{0,80}(terminate|termination))"
    )
    if not re.search(termination_notice_pattern, text, flags=re.DOTALL):
        missing.append("termination_notice")

    if not re.search(r"(cure\s+period|opportunity\s+to\s+cure)", text, flags=re.DOTALL):
        missing.append("cure_period")

    liability_cap_pattern = r"(liability).{0,80}(cap|limit|shall not exceed|maximum)"
    if not re.search(liability_cap_pattern, text, flags=re.DOTALL):
        missing.append("liability_cap")

    breach_notification_pattern = r"(data breach|breach).{0,80}(notify|notification).{0,40}(hours|days)"
    if not re.search(breach_notification_pattern, text, flags=re.DOTALL):
        missing.append("breach_notification_window")

    ip_retained_pattern = r"(pre-existing|background)\s+ip|retain(?:s|ed)?\s+(?:all\s+)?(rights?|title|interest)"
    if not re.search(ip_retained_pattern, text, flags=re.DOTALL):
        missing.append("ip_retained")

    return missing

