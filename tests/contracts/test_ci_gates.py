#!/usr/bin/env python3
"""Contract tests: .github/workflows/check.yml — every CI gate must stay on
disk, and the pinned import-linter validator must still pass on the live
config. Read-only on the real repo.

Grounding drift vs the original plan: check.yml has no unittest step yet (the
unittest gate lives in tests/e2e/test_ci_jobs.py), and the check/lints jobs
invoke the checkers without -I.
"""

from __future__ import annotations

import configparser
import unittest
from pathlib import Path

from tests._support import REPO_ROOT, load_script

WORKFLOW = REPO_ROOT / ".github" / "workflows" / "check.yml"
CONTRACTS = REPO_ROOT / "lints" / "import-linter.toml"
RUFF_TOML = REPO_ROOT / "lints" / "ruff.toml"
VIOLATIONS = REPO_ROOT / "lints" / "check" / "violations.py"


def validate_contract_config(path):
    """Mirror the CI validator body's strengthened assertions against a config;
    presence is checked by contract TYPE, compensating for the workflow's
    name-based forbidden assert (see test_forbidden_pin_uses_types)."""
    cp = configparser.ConfigParser()
    cp.read(path)
    sections = cp.sections()
    assert "importlinter" in sections, "missing [importlinter] root section"
    contracts = [s for s in sections if s.startswith("importlinter:contract:")]
    assert contracts, "no contracts found in lints/import-linter.toml"
    types = {s: cp.get(s, "type") for s in contracts}
    assert any(t == "layers" for t in types.values()), "layered contract missing"
    assert any(t == "forbidden" for t in types.values()), "domain-purity contract missing"
    for section, ctype in types.items():
        assert ctype in ("layers", "forbidden", "independence"), (
            "contract %s has invalid type %s" % (section, ctype)
        )
    return None


def workflow_text():
    return WORKFLOW.read_text(encoding="utf-8")


class CheckerSteps(unittest.TestCase):
    """Every CI job (check, lints, examples) keeps its exact entrypoint."""

    def test_check_skill_step_present(self):
        self.assertIn("python3 scripts/check-skill.py", workflow_text())

    def test_ruff_pin_present(self):
        self.assertIn('pip install "ruff==0.12.3"', workflow_text())

    def test_check_lints_step_present(self):
        self.assertIn("python3 scripts/check-lints.py", workflow_text())

    def test_check_examples_step_present(self):
        self.assertIn("python3 -I scripts/check-examples.py", workflow_text())

    def test_jobs_present(self):
        text = workflow_text()
        for job in ("  check:", "  lints:", "  examples:"):
            self.assertIn(job, text)


class ImportLinterValidator(unittest.TestCase):
    """The import-linter config gate: step exists, body pins, replica passes."""

    def test_validator_step_present(self):
        self.assertIn("name: Validate import-linter contracts config", workflow_text())

    def test_validator_body_pins(self):
        text = workflow_text()
        self.assertIn("import configparser", text)
        self.assertIn('cp.read("lints/import-linter.toml")', text)
        self.assertIn('assert "importlinter" in sections', text)
        self.assertIn("assert contracts,", text)
        # Presence checks are per TYPE, not per section name: a renamed contract
        # with the right type still satisfies the gate, a retyped one does not.
        self.assertIn('cp.get(s, "type") == "layers"', text)
        self.assertIn('cp.get(s, "type") == "forbidden"', text)

    def test_per_contract_type_pin(self):
        text = workflow_text()
        self.assertIn('cp.get(section, "type")', text)
        self.assertIn('("layers", "forbidden", "independence")', text)

    def test_replica_passes_on_live_config(self):
        self.assertIsNone(validate_contract_config(CONTRACTS))


class RuffPairing(unittest.TestCase):
    """lints/ruff.toml's select list and violations.py's expect markers pair."""

    def test_selected_rules_equal_expect_markers(self):
        mod = load_script("check-lints.py")
        rules = set(mod.selected_rules(RUFF_TOML))
        marker_codes = set()
        for _line, codes in mod.expects(VIOLATIONS):
            marker_codes.update(codes)
        self.assertTrue(rules, "no rules selected in lints/ruff.toml")
        self.assertTrue(marker_codes, "no # expect: markers in lints/check/violations.py")
        self.assertEqual(rules, marker_codes,
                         "ruff select list and violations.py expect markers drifted apart")


class UnittestGate(unittest.TestCase):
    """The unittest gate, scoped so it can never recurse into the e2e suite."""

    def test_gate_command_is_scoped_to_unit(self):
        gate_text = (REPO_ROOT / "tests" / "e2e" / "test_ci_jobs.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("-I -m unittest discover -s tests/unit -t .", gate_text)


if __name__ == "__main__":
    unittest.main()
