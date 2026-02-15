from __future__ import annotations

import unittest

from realitycheck_cli.analysis.schemas import (
    BenefitsParty,
    ClauseAnalysis,
    ClauseCategory,
    ClauseSignal,
    RiskLevel,
    Severity,
    SignalType,
)
from realitycheck_cli.scoring.power_imbalance import compute_power_imbalance
from realitycheck_cli.scoring.risk_engine import compute_contract_scores
from realitycheck_cli.scoring.leverage import (
    compute_ambiguity_index,
    compute_leverage_index,
    compute_protection_coverage,
)


def _clause(
    clause_id: str,
    category: ClauseCategory,
    risk_score: int,
    text: str,
    signals: list[ClauseSignal] | None = None,
    benefits_party: BenefitsParty = BenefitsParty.UNKNOWN,
) -> ClauseAnalysis:
    return ClauseAnalysis(
        contract_id="demo",
        clause_id=clause_id,
        title=category.value,
        page=1,
        text=text,
        category=category,
        category_confidence=0.8,
        risk_level=RiskLevel.HIGH if risk_score >= 70 else RiskLevel.MEDIUM,
        risk_score=risk_score,
        benefits_party=benefits_party,
        signals=signals or [],
        missing_protections=[],
        rewrite_suggestion="",
        negotiation_points=[],
        explanation="",
    )


class ScoringTests(unittest.TestCase):
    def test_overall_risk_score_stays_in_bounds(self) -> None:
        clauses = [
            _clause(
                clause_id="C-001",
                category=ClauseCategory.LIABILITY,
                risk_score=95,
                text="Unlimited liability applies.",
                signals=[
                    ClauseSignal(
                        type=SignalType.VAGUE_LANGUAGE,
                        label="without notice",
                        severity=Severity.HIGH,
                        evidence="without notice",
                    )
                ],
            )
        ]
        overall, _, _, _ = compute_contract_scores(
            clauses=clauses,
            missing_protections=[
                "payment_timeline",
                "termination_notice",
                "liability_cap",
            ],
            high_risk_threshold=70,
        )
        self.assertGreaterEqual(overall, 1)
        self.assertLessEqual(overall, 100)

    def test_power_imbalance_increases_for_one_sided_terms(self) -> None:
        clauses = [
            _clause(
                clause_id="C-001",
                category=ClauseCategory.TERMINATION,
                risk_score=85,
                text="Company may terminate at sole discretion without notice.",
                signals=[
                    ClauseSignal(
                        type=SignalType.ONE_SIDED_RIGHT,
                        label="termination without notice",
                        severity=Severity.HIGH,
                        evidence="terminate ... without notice",
                    )
                ],
                benefits_party=BenefitsParty.CLIENT,
            )
        ]
        score = compute_power_imbalance(clauses)
        self.assertGreaterEqual(score, 70)

    def test_ambiguity_index_scales_with_vague_language(self) -> None:
        clauses = [
            _clause(
                clause_id="C-001",
                category=ClauseCategory.TERMINATION,
                risk_score=70,
                text="Company may terminate at its sole discretion.",
                signals=[
                    ClauseSignal(
                        type=SignalType.VAGUE_LANGUAGE,
                        label="sole discretion",
                        severity=Severity.HIGH,
                        evidence="sole discretion",
                    )
                ],
            )
        ]
        ambiguity = compute_ambiguity_index(clauses)
        self.assertGreaterEqual(ambiguity, 60)

    def test_protection_coverage_penalizes_missing_items(self) -> None:
        coverage = compute_protection_coverage(
            ["payment_timeline", "liability_cap", "termination_notice"]
        )
        self.assertLess(coverage, 60)

    def test_leverage_index_combines_components(self) -> None:
        leverage = compute_leverage_index(
            overall_risk=82,
            power_imbalance=68,
            ambiguity_index=30,
            protection_coverage=60,
        )
        self.assertEqual(leverage, 35)


if __name__ == "__main__":
    unittest.main()

