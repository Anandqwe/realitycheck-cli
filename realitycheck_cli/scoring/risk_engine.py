from __future__ import annotations

from collections import defaultdict

from realitycheck_cli.analysis.schemas import ClauseAnalysis, SignalType
from realitycheck_cli.scoring.weights import CATEGORY_WEIGHTS

_CRITICAL_MISSING_KEYS = {
    "payment_timeline",
    "termination_notice",
    "liability_cap",
    "breach_notification_window",
}


def compute_contract_scores(
    clauses: list[ClauseAnalysis],
    missing_protections: list[str],
    high_risk_threshold: int = 70,
) -> tuple[int, dict[str, int], dict[str, float], list[str]]:
    category_scores = {category.value: 0 for category in CATEGORY_WEIGHTS}
    category_contributions = {category.value: 0.0 for category in CATEGORY_WEIGHTS}
    if not clauses:
        return 1, category_scores, category_contributions, []

    grouped_scores: dict[str, list[int]] = defaultdict(list)
    high_risk_clause_ids: list[str] = []
    vague_phrase_hits = 0

    for clause in clauses:
        grouped_scores[clause.category.value].append(clause.risk_score)
        if clause.risk_score >= high_risk_threshold:
            high_risk_clause_ids.append(clause.clause_id)
        for signal in clause.signals:
            if signal.type == SignalType.VAGUE_LANGUAGE:
                vague_phrase_hits += 1

    for category, weight in CATEGORY_WEIGHTS.items():
        scores = grouped_scores.get(category.value, [])
        average = round(sum(scores) / len(scores)) if scores else 0
        category_scores[category.value] = average
        category_contributions[category.value] = round(average * weight, 2)

    weighted_base = sum(category_contributions.values())
    vagueness_penalty = min(10, 2 * vague_phrase_hits)
    critical_missing_count = len(
        [item for item in missing_protections if item in _CRITICAL_MISSING_KEYS]
    )
    missing_protection_penalty = min(15, 5 * critical_missing_count)
    overall_score = round(weighted_base + vagueness_penalty + missing_protection_penalty)
    overall_score = max(1, min(100, overall_score))
    return overall_score, category_scores, category_contributions, high_risk_clause_ids

