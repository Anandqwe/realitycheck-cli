from __future__ import annotations

from typing import Any

from realitycheck_cli.analysis.heuristics import (
    detect_benefits_party,
    detect_category,
    detect_missing_protections,
    detect_signals,
    estimate_risk_score,
    risk_level_from_score,
)
from realitycheck_cli.analysis.llm_client import LLMClient
from realitycheck_cli.analysis.schemas import (
    Clause,
    ClauseAnalysis,
    ClauseCategory,
    ClauseSignal,
    RiskLevel,
    SignalType,
    Severity,
    BenefitsParty,
)
from realitycheck_cli.config.settings import Settings
from realitycheck_cli.negotiation.rewrite_suggester import (
    suggest_negotiation_points,
    suggest_rewrite,
)


def _heuristic_analysis(clause: Clause) -> ClauseAnalysis:
    category, confidence = detect_category(clause.text)
    signals = detect_signals(clause.text)
    risk_score = estimate_risk_score(category, signals)
    return ClauseAnalysis(
        contract_id=clause.contract_id,
        clause_id=clause.clause_id,
        title=clause.title,
        page=clause.page,
        text=clause.text,
        category=category,
        category_confidence=confidence,
        risk_level=risk_level_from_score(risk_score),
        risk_score=risk_score,
        benefits_party=detect_benefits_party(clause.text),
        signals=signals,
        missing_protections=[],
        rewrite_suggestion="",
        negotiation_points=[],
        explanation="Pattern-based legal risk classification.",
    )


def _serialize_heuristic(analysis: ClauseAnalysis) -> dict[str, Any]:
    return {
        "category": analysis.category.value,
        "category_confidence": analysis.category_confidence,
        "risk_level": analysis.risk_level.value,
        "risk_score": analysis.risk_score,
        "benefits_party": analysis.benefits_party.value,
        "signals": [signal.model_dump(mode="json") for signal in analysis.signals],
        "explanation": analysis.explanation,
    }


def _parse_signal(raw: dict[str, Any]) -> ClauseSignal:
    required_keys = {"type", "label", "severity", "evidence"}
    missing = required_keys.difference(raw)
    if missing:
        missing_keys = ", ".join(sorted(missing))
        raise ValueError(f"LLM signal object missing keys: {missing_keys}")
    return ClauseSignal(
        type=SignalType(raw["type"]),
        label=str(raw["label"]).strip(),
        severity=Severity(raw["severity"]),
        evidence=str(raw["evidence"]).strip(),
    )


def _merge_llm_payload(
    analysis: ClauseAnalysis, llm_payload: dict[str, Any]
) -> ClauseAnalysis:
    category = ClauseCategory(llm_payload.get("category", analysis.category.value))
    risk_score = int(llm_payload.get("risk_score", analysis.risk_score))
    risk_level = RiskLevel(llm_payload.get("risk_level", analysis.risk_level.value))
    confidence = float(
        llm_payload.get("category_confidence", analysis.category_confidence)
    )
    benefits_party = BenefitsParty(
        llm_payload.get("benefits_party", analysis.benefits_party.value)
    )

    merged_signals = list(analysis.signals)
    for raw_signal in llm_payload.get("signals", []):
        if not isinstance(raw_signal, dict):
            raise ValueError("LLM signal must be a JSON object.")
        parsed_signal = _parse_signal(raw_signal)
        signal_key = (
            parsed_signal.type.value,
            parsed_signal.label.lower(),
            parsed_signal.evidence.lower(),
        )
        existing_keys = {
            (item.type.value, item.label.lower(), item.evidence.lower())
            for item in merged_signals
        }
        if signal_key not in existing_keys:
            merged_signals.append(parsed_signal)

    explanation = str(llm_payload.get("explanation", analysis.explanation)).strip()
    return analysis.model_copy(
        update={
            "category": category,
            "risk_score": max(0, min(100, risk_score)),
            "risk_level": risk_level,
            "category_confidence": max(0.0, min(1.0, confidence)),
            "benefits_party": benefits_party,
            "signals": merged_signals,
            "explanation": explanation,
        }
    )


def analyze_clauses(
    contract_id: str,
    clauses: list[Clause],
    settings: Settings,
    use_llm: bool = False,
) -> tuple[list[ClauseAnalysis], list[str]]:
    llm_client = LLMClient(settings) if use_llm else None
    analyses: list[ClauseAnalysis] = []
    for clause in clauses:
        heuristic = _heuristic_analysis(clause)
        enriched = heuristic
        if llm_client is not None:
            payload = llm_client.classify_clause(
                clause,
                heuristic_snapshot=_serialize_heuristic(heuristic),
            )
            enriched = _merge_llm_payload(heuristic, payload)
        enriched = enriched.model_copy(
            update={
                "rewrite_suggestion": suggest_rewrite(enriched),
                "negotiation_points": suggest_negotiation_points(enriched),
            }
        )
        analyses.append(enriched)

    missing_protections = detect_missing_protections(clauses)
    return analyses, missing_protections

