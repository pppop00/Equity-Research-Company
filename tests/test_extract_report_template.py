# -*- coding: utf-8 -*-
"""
Tests for scripts/extract_report_template.py — CN / EN locked HTML extraction.

运行方式 (from repo root) / How to run (from repo root):
  python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import hashlib
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "extract_report_template.py"


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "extract_report_template", SCRIPT
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


ert = _load_module()


class TestExtractCnTemplate(unittest.TestCase):
    """中文模板：从 report_writer_cn.md 抽取锁定 HTML。"""

    def test_extracts_non_empty(self):
        md = (REPO_ROOT / "agents" / "report_writer_cn.md").read_text(
            encoding="utf-8"
        )
        html = ert.extract_html_fenced(md)
        self.assertGreater(len(html), 30_000)
        self.assertTrue(html.startswith("<!DOCTYPE html>"))
        self.assertIn('lang="zh-CN"', html)

    def test_contains_canonical_sections_and_charts(self):
        md = (REPO_ROOT / "agents" / "report_writer_cn.md").read_text(
            encoding="utf-8"
        )
        html = ert.extract_html_fenced(md)
        for fragment in (
            'id="section-summary"',
            'id="chart-waterfall"',
            'id="chart-sankey-actual"',
            "waterfallData = {{WATERFALL_JS_DATA}}",
            "const sankeyActualData = {{SANKEY_ACTUAL_JS_DATA}}",
        ):
            self.assertIn(fragment, html)

    def test_placeholders_remain_for_agent_fill(self):
        md = (REPO_ROOT / "agents" / "report_writer_cn.md").read_text(
            encoding="utf-8"
        )
        html = ert.extract_html_fenced(md)
        self.assertGreater(html.count("{{"), 20)
        self.assertIn("{{COMPANY_NAME_CN}}", html)


class TestExtractEnTemplate(unittest.TestCase):
    """English template: extract locked HTML from report_writer_en.md."""

    def test_extracts_non_empty(self):
        md = (REPO_ROOT / "agents" / "report_writer_en.md").read_text(
            encoding="utf-8"
        )
        html = ert.extract_html_fenced(md)
        self.assertGreater(len(html), 30_000)
        self.assertTrue(html.startswith("<!DOCTYPE html>"))
        self.assertIn('lang="en-US"', html)

    def test_same_structural_anchors_as_cn(self):
        md_en = (REPO_ROOT / "agents" / "report_writer_en.md").read_text(
            encoding="utf-8"
        )
        html_en = ert.extract_html_fenced(md_en)
        for fragment in (
            'id="section-porter"',
            'id="chart-radar-forward"',
            "toggleTheme",
            "redrawAllCharts",
        ):
            self.assertIn(fragment, html_en)

    def test_en_placeholders(self):
        md = (REPO_ROOT / "agents" / "report_writer_en.md").read_text(
            encoding="utf-8"
        )
        html = ert.extract_html_fenced(md)
        self.assertIn("{{RATING_EN}}", html)
        self.assertIn("{{CONFIDENCE_EN}}", html)


class TestSha256Stable(unittest.TestCase):
    """同一 .md 输入应得到稳定的 UTF-8 字节序列（便于审计日志）。"""

    def test_cn_hash_matches_known_snapshot(self):
        md = (REPO_ROOT / "agents" / "report_writer_cn.md").read_text(
            encoding="utf-8"
        )
        html = ert.extract_html_fenced(md)
        digest = hashlib.sha256(html.encode("utf-8")).hexdigest()
        # 若有意更新 agents/report_writer_cn.md 内模板，需同步改此期望值 / If the fenced template in the md changes, update this expectation.
        self.assertEqual(
            digest,
            "42014426242f88e2736b1b4b8c9c8df71ce831f3f2be4675455195ab3c283fcf",
        )

    def test_en_hash_matches_known_snapshot(self):
        md = (REPO_ROOT / "agents" / "report_writer_en.md").read_text(
            encoding="utf-8"
        )
        html = ert.extract_html_fenced(md)
        digest = hashlib.sha256(html.encode("utf-8")).hexdigest()
        self.assertEqual(
            digest,
            "c4df06fbbe22891940015411de7aed9fb9088c7f47e03257f2e9ea8b8d9e9094",
        )


class TestCliIntegration(unittest.TestCase):
    """CLI：中英文 --lang 退出码与输出文件。"""

    def _run(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT)] + args,
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )

    def test_cli_cn_writes_file(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "out.html"
            r = self._run(["--lang", "cn", "-o", str(out)])
            self.assertEqual(r.returncode, 0, msg=r.stderr)
            self.assertTrue(out.is_file())
            body = out.read_text(encoding="utf-8")
            self.assertIn("zh-CN", body)

    def test_cli_en_writes_file(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "out.html"
            r = self._run(["--lang", "en", "-o", str(out)])
            self.assertEqual(r.returncode, 0, msg=r.stderr)
            body = out.read_text(encoding="utf-8")
            self.assertIn("en-US", body)

    def test_cli_sha256_on_stderr(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "sink.html"
            r = self._run(["--lang", "cn", "--sha256", "-o", str(out)])
            self.assertEqual(r.returncode, 0, msg=r.stderr)
            self.assertIn("sha256=", r.stderr)


if __name__ == "__main__":
    unittest.main()
