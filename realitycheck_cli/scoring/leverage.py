from __future__ import annotations

from realitycheck_cli.analysis.schemas import ClauseAnalysis, Severity, SignalType

_AMBIGUITY_POINTS = {
    Severity.LOW: 1,
    Severity.MEDIUM: 2,
    Severity.HIGH: 3,
}

_PROTECTION_WEIGHTS = {
    "payment_timeline": 20,
    "liability_cap": 25,
    "termination_notice": 15,
    "cure_period": 10,
    "breach_notification_window": 15,
    "ip_retained": 15,
}


def compute_ambiguity_index(clauses: list[ClauseAnalysis]) -> int:
    if not clauses:
        return 0
    ambiguity_points = 0
    for clause in clauses:
        for signal in clause.signals:
            if signal.type == SignalType.VAGUE_LANGUAGE:
                ambiguity_points += _AMBIGUITY_POINTS.get(signal.severity, 0)
    max_points = max(1, len(clauses) * 3)
    ratio = min(1.0, ambiguity_points / max_points)
    return max(0, min(100, round(ratio * 100)))


def compute_protection_coverage(missing_protections: list[str]) -> int:
    penalty = sum(_PROTECTION_WEIGHTS.get(item, 0) for item in missing_protections)
    coverage = 100 - penalty
    return max(0, min(100, coverage))


def compute_leverage_index(
    overall_risk: int,
    power_imbalance: int,
    ambiguity_index: int,
    protection_coverage: int,
) -> int:
    leverage = (
        0.45 * (100 - overall_risk)
        + 0.25 * (100 - power_imbalance)
        + 0.20 * protection_coverage
        + 0.10 * (100 - ambiguity_index)
    )
    return max(0, min(100, round(leverage)))
