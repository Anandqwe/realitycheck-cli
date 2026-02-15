from __future__ import annotations

import re

from realitycheck_cli.analysis.schemas import (
    ClauseAnalysis,
    ClauseCategory,
    ClauseDelta,
    ComparisonFlag,
    ComparisonResult,
    ContractAnalysisResult,
    DeltaType,
    Severity,
)
from realitycheck_cli.clauses.normalizer import normalize_clause_text
from realitycheck_cli.comparison.matcher import match_clauses

_LIABILITY_EXPANSION_PATTERNS = (
    r"\bunlimited liability\b",
    r"\bliability shall not be limited\b",
    r"\bindemnif(?:y|ication).{0,40}all\b",
)
_NON_COMPETE_DURATION_RE = re.compile(
    r"(\d+)\s*(day|days|month|months|year|years)", re.IGNORECASE
)


def _duration_in_months(text: str) -> int:
    months = 0
    for amount_raw, unit in _NON_COMPETE_DURATION_RE.findall(text):
        amount = int(amount_raw)
        unit_lower = unit.lower()
        if unit_lower.startswith("day"):
            months = max(months, max(1, amount // 30))
        elif unit_lower.startswith("month"):
            months = max(months, amount)
        elif unit_lower.startswith("year"):
            months = max(months, amount * 12)
    return months


def _has_liability_expansion(text: str) -> bool:
    lowered = text.lower()
    return any(re.search(pattern, lowered) for pattern in _LIABILITY_EXPANSION_PATTERNS)


def _severity_from_risk(score: int) -> Severity:
    if score >= 85:
        return Severity.HIGH
    if score >= 65:
        return Severity.MEDIUM
    return Severity.LOW


def _build_modified_delta_reason(
    baseline_clause: ClauseAnalysis,
    revised_clause: ClauseAnalysis,
    risk_delta: int,
) -> str:
    if risk_delta > 0:
        return (
            f"Clause changed and risk increased from {baseline_clause.risk_score} "
            f"to {revised_clause.risk_score}."
        )
    if risk_delta < 0:
        return (
            f"Clause changed and risk decreased from {baseline_clause.risk_score} "
            f"to {revised_clause.risk_score}."
        )
    return "Clause text changed with neutral risk impact."


def compare_contract_results(
    baseline: ContractAnalysisResult,
    revised: ContractAnalysisResult,
    high_risk_threshold: int = 70,
) -> ComparisonResult:
    deltas: list[ClauseDelta] = []
    flags: list[ComparisonFlag] = []

    for match in match_clauses(baseline.clauses, revised.clauses):
        baseline_clause = match.baseline
        revised_clause = match.revised

        if baseline_clause is None and revised_clause is not None:
            deltas.append(
                ClauseDelta(
                    delta_type=DeltaType.ADDED,
                    baseline_clause_id=None,
                    revised_clause_id=revised_clause.clause_id,
                    risk_delta=revised_clause.risk_score,
                    reason="New clause introduced in revised contract.",
                )
            )
            if revised_clause.risk_score >= high_risk_threshold:
                flags.append(
                    ComparisonFlag(
                        type="NEW_RISK",
                        clause_id=revised_clause.clause_id,
                        description=(
                            f"Added high-risk clause ({revised_clause.title}) with risk "
                            f"{revised_clause.risk_score}."
                        ),
                        severity=_severity_from_risk(revised_clause.risk_score),
                    )
                )
            continue

        if baseline_clause is not None and revised_clause is None:
            deltas.append(
                ClauseDelta(
                    delta_type=DeltaType.REMOVED,
                    baseline_clause_id=baseline_clause.clause_id,
                    revised_clause_id=None,
                    risk_delta=-baseline_clause.risk_score,
                    reason="Clause removed from revised contract.",
                )
            )
            continue

        baseline_text = normalize_clause_text(baseline_clause.text)
        revised_text = normalize_clause_text(revised_clause.text)
        if baseline_text == revised_text:
            deltas.append(
                ClauseDelta(
                    delta_type=DeltaType.UNCHANGED,
                    baseline_clause_id=baseline_clause.clause_id,
                    revised_clause_id=revised_clause.clause_id,
                    risk_delta=0,
                    reason="Clause unchanged.",
                )
            )
        else:
            risk_delta = revised_clause.risk_score - baseline_clause.risk_score
            deltas.append(
                ClauseDelta(
                    delta_type=DeltaType.MODIFIED,
                    baseline_clause_id=baseline_clause.clause_id,
                    revised_clause_id=revised_clause.clause_id,
                    risk_delta=risk_delta,
                    reason=_build_modified_delta_reason(
                        baseline_clause=baseline_clause,
                        revised_clause=revised_clause,
                        risk_delta=risk_delta,
                    ),
                )
            )
            if risk_delta >= 20:
                flags.append(
                    ComparisonFlag(
                        type="NEW_RISK",
                        clause_id=revised_clause.clause_id,
                        description=(
                            "Modified clause materially increased legal risk."
                        ),
                        severity=_severity_from_risk(revised_clause.risk_score),
                    )
                )

        if (
            baseline_clause.category == ClauseCategory.LIABILITY
            and revised_clause.category == ClauseCategory.LIABILITY
            and (
                _has_liability_expansion(revised_clause.text)
                and (
                    not _has_liability_expansion(baseline_clause.text)
                    or revised_clause.risk_score > baseline_clause.risk_score
                )
            )
        ):
            flags.append(
                ComparisonFlag(
                    type="EXPANDED_LIABILITY",
                    clause_id=revised_clause.clause_id,
                    description="Liability language expanded in revised contract.",
                    severity=Severity.HIGH,
                )
            )

        if (
            baseline_clause.category == ClauseCategory.NON_COMPETE
            and revised_clause.category == ClauseCategory.NON_COMPETE
        ):
            baseline_months = _duration_in_months(baseline_clause.text)
            revised_months = _duration_in_months(revised_clause.text)
            if revised_months > baseline_months and revised_months > 0:
                flags.append(
                    ComparisonFlag(
                        type="EXTENDED_NON_COMPETE",
                        clause_id=revised_clause.clause_id,
                        description=(
                            f"Non-compete duration increased from {baseline_months} to {revised_months} months."
                        ),
                        severity=Severity.HIGH,
                    )
                )

    overall_delta = revised.summary.overall_risk_score - baseline.summary.overall_risk_score
    leverage_delta = revised.summary.leverage_index - baseline.summary.leverage_index
    return ComparisonResult(
        baseline_contract_id=baseline.contract_id,
        revised_contract_id=revised.contract_id,
        baseline_overall_risk=baseline.summary.overall_risk_score,
        revised_overall_risk=revised.summary.overall_risk_score,
        overall_risk_delta=overall_delta,
        baseline_leverage_index=baseline.summary.leverage_index,
        revised_leverage_index=revised.summary.leverage_index,
        leverage_delta=leverage_delta,
        deltas=deltas,
        flags=flags,
    )

