from __future__ import annotations

from realitycheck_cli.analysis.schemas import ClauseAnalysis


def generate_negotiation_email(
    contract_name: str,
    clauses: list[ClauseAnalysis],
    overall_risk_score: int,
    missing_protections: list[str],
) -> str:
    top_risks = sorted(clauses, key=lambda item: item.risk_score, reverse=True)[:3]
    lines = [
        f"Subject: Proposed revisions for {contract_name}",
        "",
        "Hi [Counterparty Name],",
        "",
        "Thank you for sharing the agreement. We reviewed it and would like to align on a few updates before signing.",
        "",
        f"Current overall risk score: {overall_risk_score}/100.",
        "",
        "Priority clauses to discuss:",
    ]
    for clause in top_risks:
        lines.append(
            f"- {clause.title} ({clause.clause_id}, risk {clause.risk_score}/100): {clause.rewrite_suggestion}"
        )
    if missing_protections:
        lines.extend(
            [
                "",
                "Additional protections requested:",
                *[f"- Add explicit language for: {item.replace('_', ' ')}" for item in missing_protections],
            ]
        )
    lines.extend(
        [
            "",
            "Happy to share redlines and discuss alternatives that work for both parties.",
            "",
            "Best regards,",
            "[Your Name]",
        ]
    )
    return "\n".join(lines)

