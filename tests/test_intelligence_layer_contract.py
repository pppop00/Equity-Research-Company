# -*- coding: utf-8 -*-
"""Contract tests for the report-facing intelligence layer."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestIntelligenceLayerReference(unittest.TestCase):
    def test_reference_exists_and_names_signal_types(self):
        ref = REPO_ROOT / "references" / "intelligence_layer.md"
        self.assertTrue(ref.is_file())
        text = ref.read_text(encoding="utf-8")
        for signal_type in (
            "filing_disclosure",
            "industry_shift",
            "company_event",
            "policy_regulation",
            "customer_supply_chain",
            "pricing_margin",
            "consensus_trap",
        ):
            self.assertIn(signal_type, text)
        for field in (
            "affected_metric",
            "watch_metric",
            "thesis_implication",
        ):
            self.assertIn(field, text)


class TestAgentContracts(unittest.TestCase):
    def test_news_researcher_outputs_intelligence_signals(self):
        text = (REPO_ROOT / "agents" / "news_researcher.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("references/intelligence_layer.md", text)
        self.assertIn('"intelligence_signals"', text)
        for field in (
            '"id"',
            '"signal_type"',
            '"affected_metric"',
            '"watch_metric"',
            '"thesis_implication"',
        ):
            self.assertIn(field, text)

    def test_edge_insight_requires_monitor_and_falsification(self):
        text = (REPO_ROOT / "agents" / "edge_insight_writer.md").read_text(
            encoding="utf-8"
        )
        for field in (
            "chosen_signal_ids",
            "thesis_variable",
            "monitor_metric",
            "falsification_trigger",
        ):
            self.assertIn(field, text)

    def test_phase_and_validator_consume_signal_layer(self):
        phase_rules = (
            REPO_ROOT / "references" / "phase_execution_rules.md"
        ).read_text(encoding="utf-8")
        validator = (REPO_ROOT / "agents" / "report_validator.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("source_signal_id", phase_rules)
        self.assertIn("intelligence_signals", validator)
        self.assertIn("falsification_trigger", validator)


if __name__ == "__main__":
    unittest.main()
