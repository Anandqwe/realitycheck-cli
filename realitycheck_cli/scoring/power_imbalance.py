from __future__ import annotations

from realitycheck_cli.analysis.schemas import BenefitsParty, ClauseAnalysis, SignalType

_MUTUALITY_MARKERS = ("mutual", "both parties", "each party")
_NOTICE_MARKERS = ("written notice", "notice period", "days notice")


def compute_power_imbalance(clauses: list[ClauseAnalysis]) -> int:
    unilateral_rights = 0
    asymmetric_obligations = 0
    sole_discretion_terms = 0
    mutuality_markers = 0
    notice_protections = 0

    for clause in clauses:
        lowered = clause.text.lower()
        if clause.benefits_party in (BenefitsParty.CLIENT, BenefitsParty.VENDOR):
            asymmetric_obligations += 1
        if "sole discretion" in lowered:
            sole_discretion_terms += 1
        if "without notice" in lowered:
            unilateral_rights += 1
        if any(marker in lowered for marker in _MUTUALITY_MARKERS):
            mutuality_markers += 1
        if any(marker in lowered for marker in _NOTICE_MARKERS):
            notice_protections += 1
        for signal in clause.signals:
            if signal.type == SignalType.ONE_SIDED_RIGHT:
                unilateral_rights += 1

    score = (
        50
        + (8 * unilateral_rights)
        + (6 * asymmetric_obligations)
        + (4 * sole_discretion_terms)
        - (5 * mutuality_markers)
        - (4 * notice_protections)
    )
    return max(0, min(100, score))

