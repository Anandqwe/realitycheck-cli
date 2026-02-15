from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher

from realitycheck_cli.analysis.schemas import ClauseAnalysis
from realitycheck_cli.clauses.normalizer import canonical_title, normalize_clause_text


@dataclass(frozen=True)
class ClauseMatch:
    baseline: ClauseAnalysis | None
    revised: ClauseAnalysis | None
    similarity: float


def _score_match(baseline: ClauseAnalysis, revised: ClauseAnalysis) -> float:
    title_similarity = SequenceMatcher(
        None,
        canonical_title(baseline.title),
        canonical_title(revised.title),
    ).ratio()
    baseline_text = normalize_clause_text(baseline.text)[:1200]
    revised_text = normalize_clause_text(revised.text)[:1200]
    text_similarity = SequenceMatcher(None, baseline_text, revised_text).ratio()
    return (0.7 * title_similarity) + (0.3 * text_similarity)


def match_clauses(
    baseline_clauses: list[ClauseAnalysis],
    revised_clauses: list[ClauseAnalysis],
    threshold: float = 0.55,
) -> list[ClauseMatch]:
    baseline_unused = set(range(len(baseline_clauses)))
    matches: list[ClauseMatch] = []

    for revised in revised_clauses:
        best_index = None
        best_score = 0.0
        for idx in baseline_unused:
            score = _score_match(baseline_clauses[idx], revised)
            if score > best_score:
                best_score = score
                best_index = idx
        if best_index is not None and best_score >= threshold:
            matches.append(
                ClauseMatch(
                    baseline=baseline_clauses[best_index],
                    revised=revised,
                    similarity=round(best_score, 3),
                )
            )
            baseline_unused.remove(best_index)
        else:
            matches.append(ClauseMatch(baseline=None, revised=revised, similarity=0.0))

    for idx in sorted(baseline_unused):
        matches.append(
            ClauseMatch(
                baseline=baseline_clauses[idx],
                revised=None,
                similarity=0.0,
            )
        )
    return matches

