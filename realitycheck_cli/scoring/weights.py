from __future__ import annotations

from realitycheck_cli.analysis.schemas import ClauseCategory

CATEGORY_WEIGHTS: dict[ClauseCategory, float] = {
    ClauseCategory.NON_COMPETE: 0.15,
    ClauseCategory.IP_TRANSFER: 0.17,
    ClauseCategory.LIABILITY: 0.22,
    ClauseCategory.TERMINATION: 0.12,
    ClauseCategory.FINANCIAL_RISK: 0.20,
    ClauseCategory.PRIVACY: 0.09,
    ClauseCategory.NEUTRAL: 0.05,
}

