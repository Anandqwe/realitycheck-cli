from __future__ import annotations

from types import SimpleNamespace
import unittest
from unittest.mock import patch

from realitycheck_cli.analysis.llm_client import LLMClient
from realitycheck_cli.analysis.schemas import Clause
from realitycheck_cli.config.settings import Settings


class LLMClientTests(unittest.TestCase):
    @patch("realitycheck_cli.analysis.llm_client.genai.GenerativeModel")
    @patch("realitycheck_cli.analysis.llm_client.genai.configure")
    def test_classify_clause_uses_configured_timeout(
        self,
        _mock_configure,
        mock_model_class,
    ) -> None:
        model = mock_model_class.return_value
        model.generate_content.return_value = SimpleNamespace(text='{"category":"NEUTRAL"}')

        settings = Settings(
            gemini_api_key="fake-key",
            gemini_model="gemini-3-flash-preview",
            high_risk_threshold=70,
            llm_timeout_seconds=7,
        )
        client = LLMClient(settings)
        clause = Clause(
            contract_id="demo",
            clause_id="C-001",
            title="Title",
            page=1,
            text="Some text",
        )

        result = client.classify_clause(clause, heuristic_snapshot={})

        self.assertEqual(result["category"], "NEUTRAL")
        _, kwargs = model.generate_content.call_args
        self.assertEqual(kwargs["request_options"]["timeout"], 7)


if __name__ == "__main__":
    unittest.main()
