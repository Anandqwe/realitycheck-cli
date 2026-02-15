from __future__ import annotations

import unittest

from realitycheck_cli.analysis.heuristics import detect_missing_protections, detect_signals
from realitycheck_cli.analysis.schemas import Clause, SignalType


class HeuristicsTests(unittest.TestCase):
    def test_detects_vague_language(self) -> None:
        text = (
            "Company may terminate this agreement at its sole discretion "
            "and without notice."
        )
        signals = detect_signals(text)
        vague = [signal for signal in signals if signal.type == SignalType.VAGUE_LANGUAGE]
        self.assertTrue(vague)

    def test_detects_missing_protections(self) -> None:
        clauses = [
            Clause(
                contract_id="demo",
                clause_id="C-001",
                title="Services",
                page=1,
                text="Provider will deliver software services and support.",
            )
        ]
        missing = detect_missing_protections(clauses)
        self.assertIn("payment_timeline", missing)
        self.assertIn("termination_notice", missing)


if __name__ == "__main__":
    unittest.main()

