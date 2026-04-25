# -*- coding: utf-8 -*-
"""
Tests for workflow_meta.json validation.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "validate_workflow_meta.py"
META = REPO_ROOT / "workflow_meta.json"


class TestWorkflowMeta(unittest.TestCase):
    def test_meta_file_exists(self):
        self.assertTrue(META.is_file())

    def test_validator_passes_on_repo_meta(self):
        r = subprocess.run(
            [sys.executable, str(SCRIPT), "--meta", str(META)],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        self.assertIn("OK:", r.stdout)

    def test_validator_fails_on_missing_key(self):
        bad_meta = '{"version":"1.0.0"}'
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "bad.json"
            p.write_text(bad_meta, encoding="utf-8")
            r = subprocess.run(
                [sys.executable, str(SCRIPT), "--meta", str(p)],
                capture_output=True,
                text=True,
                cwd=str(REPO_ROOT),
            )
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("missing top-level keys", r.stderr)


if __name__ == "__main__":
    unittest.main()
