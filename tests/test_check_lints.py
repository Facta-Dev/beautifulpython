#!/usr/bin/env python3
"""Tests for scripts/check-lints.py."""

from __future__ import annotations

import importlib.util
import shutil
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "check-lints.py"
HAS_RUFF = shutil.which("ruff") is not None


def load_checker():
    spec = importlib.util.spec_from_file_location("check_lints", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load %s" % SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


cl = load_checker()

CONFIG = """\
target-version = "py312"

[lint]
select = [
  "E722",  # bare except
  "S101",  # bare assert
]
"""

VIOLATIONS = '''\
"""One deliberate violation per lint."""

def guard(x):
    assert x  # expect: S101
    try:
        return int(x)
    except:  # expect: E722
        return 0
'''


class HelpersTest(unittest.TestCase):
    def test_selected_rules_reads_the_select_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "ruff.toml"
            config.write_text(CONFIG, encoding="utf-8")
            rules = cl.selected_rules(config)
        self.assertEqual(rules, {"E722": 5, "S101": 6})

    def test_expects_read_markers(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "violations.py"
            path.write_text(VIOLATIONS, encoding="utf-8")
            found = cl.expects(path)
        self.assertEqual([(n, sorted(c)) for n, c in found], [(4, ["S101"]), (7, ["E722"])])


class CheckTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "lints" / "check").mkdir(parents=True)
        (self.root / "lints" / "ruff.toml").write_text(CONFIG, encoding="utf-8")
        (self.root / "lints" / "check" / "violations.py").write_text(VIOLATIONS, encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def write_violations(self, text):
        (self.root / "lints" / "check" / "violations.py").write_text(text, encoding="utf-8")

    @unittest.skipUnless(HAS_RUFF, "ruff is not installed")
    def test_valid_harness_passes(self):
        problems, proven = cl.check(self.root, shutil.which("ruff"))
        self.assertEqual(problems, [], problems)
        self.assertEqual(proven, 2)

    def test_missing_violations_file(self):
        (self.root / "lints" / "check" / "violations.py").unlink()
        problems, _ = cl.check(self.root, shutil.which("ruff") or "ruff")
        self.assertEqual(problems, ["missing lints/check/violations.py"])

    @unittest.skipUnless(HAS_RUFF, "ruff is not installed")
    def test_a_rule_that_stops_firing_fails(self):
        self.write_violations(VIOLATIONS.replace("    except:", "    except ValueError as e:\n        return 0  # expect: E722"))
        problems, _ = cl.check(self.root, shutil.which("ruff"))
        self.assertTrue(any("E722 did not fire" in p for p in problems), problems)

    @unittest.skipUnless(HAS_RUFF, "ruff is not installed")
    def test_an_unexpected_diagnostic_fails(self):
        extra = VIOLATIONS + "\n\n"
        extra += "def stray(x):\n"
        extra += "    try:\n"
        extra += "        return x\n"
        extra += "    except:\n"
        extra += "        return 0\n"
        self.write_violations(extra)
        problems, _ = cl.check(self.root, shutil.which("ruff"))
        self.assertTrue(any("unexpected" in p for p in problems), problems)

    def test_drift_between_config_and_violations(self):
        self.write_violations('"""none."""\n')
        problems, _ = cl.check(self.root, "ruff-missing-on-purpose")
        messages = " ".join(problems)
        self.assertIn("E722 is selected but has no violation", messages)
        self.assertIn("S101 is selected but has no violation", messages)

    def test_expect_code_not_selected(self):
        self.write_violations(VIOLATIONS.replace("expect: S101", "expect: T201"))
        problems, _ = cl.check(self.root, "ruff-missing-on-purpose")
        self.assertTrue(any("T201 is not selected" in p for p in problems), problems)

    def test_this_repo_harness_passes_offline_checks(self):
        problems, _ = cl.check(REPO_ROOT, "ruff-not-required-here")
        self.assertEqual(
            [p for p in problems if "selected but has no violation" in p or "is not selected" in p],
            [],
            [p for p in problems if "selected" in p],
        )


if __name__ == "__main__":
    unittest.main()
