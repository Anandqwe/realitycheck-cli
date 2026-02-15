from __future__ import annotations

from realitycheck_cli.analysis.schemas import ClauseAnalysis, ClauseCategory, SignalType

_CATEGORY_REWRITES: dict[ClauseCategory, str] = {
    ClauseCategory.NON_COMPETE: (
        "Limit non-compete scope by duration, geography, and direct competitor definition."
    ),
    ClauseCategory.IP_TRANSFER: (
        "Narrow IP assignment to deliverables created under this agreement and keep pre-existing IP excluded."
    ),
    ClauseCategory.LIABILITY: (
        "Add a reasonable liability cap and exclude consequential damages except for willful misconduct."
    ),
    ClauseCategory.TERMINATION: (
        "Require written notice and a cure period before termination for non-material breaches."
    ),
    ClauseCategory.FINANCIAL_RISK: (
        "Define clear payment milestones, invoice timing, and late-payment consequences."
    ),
    ClauseCategory.PRIVACY: (
        "Specify data handling boundaries, breach notice deadlines, and security obligations."
    ),
    ClauseCategory.NEUTRAL: "Clarify ambiguous terms and add measurable obligations.",
}


def suggest_rewrite(clause: ClauseAnalysis) -> str:
    base = _CATEGORY_REWRITES.get(clause.category, _CATEGORY_REWRITES[ClauseCategory.NEUTRAL])
    if any(signal.type == SignalType.VAGUE_LANGUAGE for signal in clause.signals):
        return (
            f"{base} Replace vague expressions with objective triggers, deadlines, and defined terms."
        )
    return base


def suggest_negotiation_points(clause: ClauseAnalysis) -> list[str]:
    points: list[str] = []
    for signal in clause.signals:
        if signal.type == SignalType.VAGUE_LANGUAGE:
            points.append("Request objective criteria instead of discretionary wording.")
        if signal.type == SignalType.ONE_SIDED_RIGHT:
            points.append("Ask for reciprocity so rights and obligations are balanced.")
        if signal.type == SignalType.LIABILITY_EXPANSION:
            points.append("Request a liability cap and carve-outs only for intentional misconduct.")
    if clause.risk_score >= 80:
        points.append("Propose a redline before signature due to critical legal exposure.")
    if not points:
        points.append("Confirm this clause aligns with your commercial and legal objectives.")
    return points[:3]

