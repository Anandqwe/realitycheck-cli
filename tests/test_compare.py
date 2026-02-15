from __future__ import annotations

import unittest

from realitycheck_cli.analysis.schemas import (
    BenefitsParty,
    ClauseAnalysis,
    ClauseCategory,
    ContractAnalysisResult,
    ContractRiskSummary,
    RiskLevel,
)
from realitycheck_cli.comparison.delta_engine import compare_contract_results


def _analysis(
    clause_id: str,
    title: str,
    text: str,
    category: ClauseCategory,
    risk: int,
) -> ClauseAnalysis:
    return ClauseAnalysis(
        contract_id="demo",
        clause_id=clause_id,
        title=title,
        page=1,
        text=text,
        category=category,
        category_confidence=0.85,
        risk_level=RiskLevel.HIGH if risk >= 70 else RiskLevel.MEDIUM,
        risk_score=risk,
        benefits_party=BenefitsParty.UNKNOWN,
        signals=[],
        missing_protections=[],
        rewrite_suggestion="",
        negotiation_points=[],
        explanation="",
    )


def _result(contract_id: str, clauses: list[ClauseAnalysis], overall_risk: int) -> ContractAnalysisResult:
    summary = ContractRiskSummary(
        contract_id=contract_id,
        overall_risk_score=overall_risk,
        power_imbalance_score=50,
        ambiguity_index=0,
        protection_coverage_score=100,
        leverage_index=50,
        category_scores={},
        weighted_contributions={},
        high_risk_clause_ids=[clause.clause_id for clause in clauses if clause.risk_score >= 70],
        missing_protections=[],
    )
    return ContractAnalysisResult(
        contract_id=contract_id,
        source_path=f"{contract_id}.pdf",
        clauses=clauses,
        summary=summary,
        negotiation_email="",
    )


class CompareTests(unittest.TestCase):
    def test_detects_new_and_expanded_risk_flags(self) -> None:
        baseline = _result(
            contract_id="baseline",
            overall_risk=45,
            clauses=[
                _analysis(
                    clause_id="C-001",
                    title="Non-Compete",
                    text="Contractor agrees to a 12 month non-compete term.",
                    category=ClauseCategory.NON_COMPETE,
                    risk=55,
                ),
                _analysis(
                    clause_id="C-002",
                    title="Liability",
                    text="Liability is capped at fees paid in the last 12 months.",
                    category=ClauseCategory.LIABILITY,
                    risk=60,
                ),
            ],
        )
        revised = _result(
            contract_id="revised",
            overall_risk=78,
            clauses=[
                _analysis(
                    clause_id="C-001",
                    title="Non-Compete",
                    text="Contractor agrees to a 24 month non-compete term.",
                    category=ClauseCategory.NON_COMPETE,
                    risk=78,
                ),
                _analysis(
                    clause_id="C-002",
                    title="Liability",
                    text="The contractor accepts unlimited liability for all damages.",
                    category=ClauseCategory.LIABILITY,
                    risk=92,
                ),
                _analysis(
                    clause_id="C-003",
                    title="Audit",
                    text="Client may audit records at any time for any reason and without notice.",
                    category=ClauseCategory.PRIVACY,
                    risk=85,
                ),
            ],
        )

        comparison = compare_contract_results(baseline=baseline, revised=revised)
        flag_types = {flag.type for flag in comparison.flags}
        self.assertIn("NEW_RISK", flag_types)
        self.assertIn("EXPANDED_LIABILITY", flag_types)
        self.assertIn("EXTENDED_NON_COMPETE", flag_types)


if __name__ == "__main__":
    unittest.main()

