# -*- coding: utf-8 -*-
"""
Tests for references/analyst_call.schema.json — the analyst_call.json sidecar
introduced in plan v3 (analyst-voice-v2). The schema fixes downstream card
prose drift toward clickbait by formalising the analyst layer (call /
variant view / catalysts / falsifiers / primary quotes / asymmetry).

How to run (from repo root):
  python3 -m unittest tests.test_analyst_call -v
"""
from __future__ import annotations

import copy
import json
import re
import unittest
from pathlib import Path

try:
    import jsonschema
    from jsonschema import Draft7Validator
    HAS_JSONSCHEMA = True
except ImportError:  # pragma: no cover - jsonschema is in env per harness setup
    HAS_JSONSCHEMA = False

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "references" / "analyst_call.schema.json"
FIXTURE_VALID = REPO_ROOT / "tests" / "fixtures" / "analyst_call_valid.json"


def _load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _load_valid_fixture() -> dict:
    return json.loads(FIXTURE_VALID.read_text(encoding="utf-8"))


def _validate(instance: dict, schema: dict) -> list[str]:
    """Return a list of validation error messages. Empty list = valid."""
    if HAS_JSONSCHEMA:
        validator = Draft7Validator(schema)
        return [e.message for e in validator.iter_errors(instance)]
    # Hand-rolled minimal fallback so the test still has signal without jsonschema.
    errors: list[str] = []
    required = schema.get("required", [])
    for key in required:
        if key not in instance:
            errors.append(f"missing required key: {key}")
    if schema.get("additionalProperties") is False:
        allowed = set(schema.get("properties", {}).keys())
        for k in instance.keys():
            if k not in allowed:
                errors.append(f"unknown top-level key: {k}")
    call = instance.get("call")
    call_enum = (
        schema.get("properties", {}).get("call", {}).get("enum", [])
    )
    if call_enum and call not in call_enum:
        errors.append(f"call not in enum: {call}")
    conv = instance.get("conviction")
    if isinstance(conv, int) and (conv < 1 or conv > 5):
        errors.append(f"conviction out of range: {conv}")
    for list_key in ("variant_view", "catalysts_positive", "falsifiers", "primary_quotes"):
        if list_key in instance and isinstance(instance[list_key], list):
            if len(instance[list_key]) < 1:
                errors.append(f"{list_key} is empty")
    if "variant_view" in instance and isinstance(instance["variant_view"], list):
        for i, s in enumerate(instance["variant_view"]):
            if isinstance(s, str) and len(s) < 30:
                errors.append(f"variant_view[{i}] too short")
    if "comp_anchors" in instance and isinstance(instance["comp_anchors"], list):
        for i, anchor in enumerate(instance["comp_anchors"]):
            if not isinstance(anchor, dict):
                continue
            keys = set(anchor.keys())
            has_extra = (
                "management_guide" in keys
                or any(k.startswith("peer_") for k in keys)
                or any(re.match(r"^historical_[0-9]+y_avg$", k) for k in keys)
            )
            if not has_extra:
                errors.append(f"comp_anchors[{i}] missing peer/historical/guide")
    return errors


# ----------------------- Schema-level tests -----------------------


class TestSchemaItself(unittest.TestCase):
    """The schema file is well-formed and registers as Draft-07."""

    def test_schema_file_exists(self):
        self.assertTrue(SCHEMA_PATH.is_file(), f"missing {SCHEMA_PATH}")

    def test_schema_is_valid_json(self):
        schema = _load_schema()
        self.assertIsInstance(schema, dict)
        self.assertEqual(
            schema.get("$schema"),
            "http://json-schema.org/draft-07/schema#",
        )
        self.assertEqual(schema.get("type"), "object")
        self.assertEqual(
            schema.get("title"),
            "Analyst Call Sidecar (analyst_call.json)",
        )

    def test_schema_self_validates_as_draft7(self):
        if not HAS_JSONSCHEMA:
            self.skipTest("jsonschema not installed")
        schema = _load_schema()
        # Will raise SchemaError if the schema itself is malformed.
        Draft7Validator.check_schema(schema)

    def test_top_level_required_fields(self):
        schema = _load_schema()
        required = set(schema["required"])
        expected = {
            "schema_version",
            "call",
            "conviction",
            "horizon_months",
            "consensus_view",
            "variant_view",
            "key_number",
            "comp_anchors",
            "catalysts_positive",
            "catalysts_negative",
            "falsifiers",
            "primary_quotes",
            "asymmetry",
        }
        self.assertEqual(required, expected)

    def test_top_level_additional_properties_false(self):
        schema = _load_schema()
        self.assertIs(schema.get("additionalProperties"), False)

    def test_each_top_level_property_has_description(self):
        schema = _load_schema()
        for name, sub in schema["properties"].items():
            self.assertIn(
                "description",
                sub,
                f"property {name!r} is missing a description (writer needs guidance)",
            )


# ----------------------- Positive fixture -----------------------


class TestPositiveFixture(unittest.TestCase):
    """The realistic NVDA-style fixture must validate cleanly."""

    def test_valid_fixture_passes(self):
        schema = _load_schema()
        instance = _load_valid_fixture()
        errors = _validate(instance, schema)
        self.assertEqual(errors, [], f"valid fixture should pass; got: {errors}")


# ----------------------- Negative fixtures -----------------------


class TestNegativeFixtures(unittest.TestCase):
    """Each defect must cause validation to fail."""

    @classmethod
    def setUpClass(cls):
        cls.schema = _load_schema()
        cls.base = _load_valid_fixture()

    def _mutate(self, mutator) -> dict:
        instance = copy.deepcopy(self.base)
        mutator(instance)
        return instance

    def _assert_fails(self, instance: dict, label: str):
        errors = _validate(instance, self.schema)
        self.assertGreater(
            len(errors),
            0,
            f"{label}: expected at least one validation error, got none",
        )

    def test_variant_view_empty(self):
        bad = self._mutate(lambda d: d.__setitem__("variant_view", []))
        self._assert_fails(bad, "empty variant_view")

    def test_variant_view_item_too_short(self):
        bad = self._mutate(lambda d: d["variant_view"].__setitem__(0, "too short"))
        self._assert_fails(bad, "variant_view[0] <30 chars")

    def test_catalysts_positive_empty(self):
        bad = self._mutate(lambda d: d.__setitem__("catalysts_positive", []))
        self._assert_fails(bad, "empty catalysts_positive")

    def test_falsifiers_empty(self):
        bad = self._mutate(lambda d: d.__setitem__("falsifiers", []))
        self._assert_fails(bad, "empty falsifiers")

    def test_primary_quotes_empty(self):
        bad = self._mutate(lambda d: d.__setitem__("primary_quotes", []))
        self._assert_fails(bad, "empty primary_quotes")

    def test_comp_anchor_missing_peer_or_historical_or_guide(self):
        bad = self._mutate(
            lambda d: d.__setitem__(
                "comp_anchors",
                [{"metric": "nearline ASP", "ours": "$24/TB"}],
            )
        )
        self._assert_fails(bad, "comp_anchors[0] only has metric+ours")

    def test_call_not_in_enum(self):
        bad = self._mutate(lambda d: d.__setitem__("call", "strong_buy"))
        self._assert_fails(bad, "call=strong_buy not in enum")

    def test_conviction_out_of_range(self):
        bad = self._mutate(lambda d: d.__setitem__("conviction", 6))
        self._assert_fails(bad, "conviction=6")

    def test_unknown_top_level_key_rejected(self):
        bad = self._mutate(lambda d: d.__setitem__("recommendation", "BUY"))
        self._assert_fails(bad, "unknown key 'recommendation'")


# ----------------------- Grounding helper -----------------------


STOPWORDS = {
    "the", "and", "for", "with", "from", "that", "this", "into", "over",
    "under", "than", "have", "will", "would", "could", "should", "their",
    "them", "they", "these", "those", "also", "more", "most", "much",
    "such", "been", "being", "were", "what", "when", "where", "while",
    "about", "above", "after", "before", "between", "during", "still",
    "then", "there", "here", "very", "some", "each", "other", "across",
    "within", "without", "because", "consensus", "street", "modeling",
    "model", "models", "expects", "expect", "expected",
}


def _tokens(text: str) -> set[str]:
    raw = re.findall(r"[A-Za-z][A-Za-z0-9_-]{3,}", text or "")
    return {t.lower() for t in raw if t.lower() not in STOPWORDS}


def variant_view_grounded(
    variant_view: list[str],
    upstream: dict[str, dict | list | str],
    min_overlap: int = 3,
) -> list[tuple[int, int, set[str]]]:
    """For each variant_view item, return (index, overlap_count, overlap_keywords).

    upstream is a dict of {file_label: json-loadable-object} (e.g. financial_data,
    financial_analysis, porter_analysis, news_intel). Cross-validator should
    require overlap_count >= 3 substantive keywords per variant_view item.
    """
    blob = " ".join(
        json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v
        for v in upstream.values()
    )
    blob_tokens = _tokens(blob)
    out: list[tuple[int, int, set[str]]] = []
    for i, item in enumerate(variant_view):
        item_tokens = _tokens(item)
        overlap = item_tokens & blob_tokens
        out.append((i, len(overlap), overlap))
    return out


class TestVariantViewGroundingSignature(unittest.TestCase):
    """Demonstrate the cross-validator grounding rule. Positive + negative path."""

    def test_positive_grounding(self):
        variant_view = [
            "Blackwell rack-scale (GB200 NVL72) shifts revenue mix to systems "
            "where ASP per GPU-equivalent is materially higher than consensus.",
        ]
        upstream = {
            "financial_data": {
                "revenue_mix": "Blackwell datacenter systems ramping",
                "nvl72_orders": "12 hyperscaler customers committed",
            },
            "financial_analysis": "GB200 systems pricing supports gross margin "
            "expansion via higher ASP per accelerator equivalent.",
            "porter_analysis": {
                "rivalry": "AMD MI355 competes on price but lacks NVLink fabric",
            },
            "news_intel": "Blackwell shipments accelerating; rack-scale demand strong",
        }
        results = variant_view_grounded(variant_view, upstream, min_overlap=3)
        self.assertEqual(len(results), 1)
        idx, overlap_count, overlap_words = results[0]
        self.assertGreaterEqual(
            overlap_count,
            3,
            f"expected >=3 overlap, got {overlap_count}: {overlap_words}",
        )

    def test_negative_grounding(self):
        variant_view = [
            "Quantum tunneling redirects fiscal momentum through narrative gravitation."
        ]
        upstream = {
            "financial_data": {"revenue": "NVDA datacenter Blackwell"},
            "financial_analysis": "GPU systems and networking attach mix shift",
            "porter_analysis": {"rivalry": "AMD MI355"},
            "news_intel": "Hyperscaler capex commentary",
        }
        results = variant_view_grounded(variant_view, upstream, min_overlap=3)
        idx, overlap_count, overlap_words = results[0]
        self.assertLess(
            overlap_count,
            3,
            f"ungrounded variant should overlap <3, got {overlap_count}: {overlap_words}",
        )

    def test_all_fixture_variant_views_ground_against_synthetic_upstream(self):
        """The valid fixture's variant_view items should ground against a
        synthetic upstream blob that mirrors what real financial_data /
        financial_analysis / porter_analysis / news_intel would contain
        for the same NVDA-style call."""
        instance = _load_valid_fixture()
        upstream = {
            "financial_data": {
                "datacenter_revenue": "Blackwell ramp; NVL72 rack-scale systems "
                "shipping; networking attach via NVLink and Spectrum-X.",
                "asp_blended": "$36k per GPU-equivalent FY27",
                "gross_margin_history": "datacenter margin 70-75% range",
            },
            "financial_analysis": "Systems mix shift lifts blended ASP; "
            "networking attach lifts gross margin; sovereign AI demand pool "
            "incremental to hyperscaler base; memory cost easing FY27.",
            "porter_analysis": {
                "rivalry": "AMD MI355 competes on price; lacks NVLink fabric",
                "buyer_power": "Hyperscaler concentration risk; sovereign AI diversifies",
            },
            "news_intel": "Rubin tape-out cadence; Blackwell systems pricing; "
            "hyperscaler capex commentary across AWS Azure GCP META.",
        }
        results = variant_view_grounded(instance["variant_view"], upstream, min_overlap=3)
        for idx, count, words in results:
            self.assertGreaterEqual(
                count,
                3,
                f"variant_view[{idx}] only overlaps {count} keywords ({words}); "
                "fixture should ground against synthetic upstream",
            )


if __name__ == "__main__":
    unittest.main()
