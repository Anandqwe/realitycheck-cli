from __future__ import annotations

from pathlib import Path

from realitycheck_cli.analysis.classifier import analyze_clauses
from realitycheck_cli.analysis.schemas import (
    ComparisonResult,
    ContractAnalysisResult,
    ContractRiskSummary,
)
from realitycheck_cli.clauses.splitter import split_into_clauses
from realitycheck_cli.comparison.delta_engine import compare_contract_results
from realitycheck_cli.config.settings import Settings
from realitycheck_cli.ingest.pdf_parser import parse_pdf
from realitycheck_cli.ingest.text_cleaner import clean_pages
from realitycheck_cli.negotiation.email_generator import generate_negotiation_email
from realitycheck_cli.scoring.leverage import (
    compute_ambiguity_index,
    compute_leverage_index,
    compute_protection_coverage,
)
from realitycheck_cli.scoring.power_imbalance import compute_power_imbalance
from realitycheck_cli.scoring.risk_engine import compute_contract_scores


def analyze_contract_file(
    pdf_path: Path,
    settings: Settings,
    use_llm: bool = False,
) -> ContractAnalysisResult:
    cleaned_pages = clean_pages(parse_pdf(pdf_path))
    contract_id = pdf_path.stem
    clauses = split_into_clauses(contract_id=contract_id, pages=cleaned_pages)
    if not clauses:
        raise ValueError(f"No clauses could be extracted from {pdf_path}.")

    clause_analyses, missing_protections = analyze_clauses(
        contract_id=contract_id,
        clauses=clauses,
        settings=settings,
        use_llm=use_llm,
    )
    (
        overall_risk,
        category_scores,
        weighted_contributions,
        high_risk_clause_ids,
    ) = compute_contract_scores(
        clauses=clause_analyses,
        missing_protections=missing_protections,
        high_risk_threshold=settings.high_risk_threshold,
    )
    power_imbalance = compute_power_imbalance(clause_analyses)
    ambiguity_index = compute_ambiguity_index(clause_analyses)
    protection_coverage = compute_protection_coverage(missing_protections)
    leverage_index = compute_leverage_index(
        overall_risk=overall_risk,
        power_imbalance=power_imbalance,
        ambiguity_index=ambiguity_index,
        protection_coverage=protection_coverage,
    )

    summary = ContractRiskSummary(
        contract_id=contract_id,
        overall_risk_score=overall_risk,
        power_imbalance_score=power_imbalance,
        ambiguity_index=ambiguity_index,
        protection_coverage_score=protection_coverage,
        leverage_index=leverage_index,
        category_scores=category_scores,
        weighted_contributions=weighted_contributions,
        high_risk_clause_ids=high_risk_clause_ids,
        missing_protections=missing_protections,
    )
    negotiation_email = generate_negotiation_email(
        contract_name=contract_id,
        clauses=clause_analyses,
        overall_risk_score=overall_risk,
        missing_protections=missing_protections,
    )
    return ContractAnalysisResult(
        contract_id=contract_id,
        source_path=str(pdf_path),
        clauses=clause_analyses,
        summary=summary,
        negotiation_email=negotiation_email,
    )


def compare_contract_files(
    baseline_path: Path,
    revised_path: Path,
    settings: Settings,
    use_llm: bool = False,
) -> tuple[ContractAnalysisResult, ContractAnalysisResult, ComparisonResult]:
    baseline_result = analyze_contract_file(
        pdf_path=baseline_path,
        settings=settings,
        use_llm=use_llm,
    )
    revised_result = analyze_contract_file(
        pdf_path=revised_path,
        settings=settings,
        use_llm=use_llm,
    )
    comparison = compare_contract_results(
        baseline=baseline_result,
        revised=revised_result,
        high_risk_threshold=settings.high_risk_threshold,
    )
    return baseline_result, revised_result, comparison

