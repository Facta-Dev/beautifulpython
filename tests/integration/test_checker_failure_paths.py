#!/usr/bin/env python3
"""Failure-path tests for the checkers: mutate a COPY of the repo, never the
real one, and prove each hardened guard fires. Each test copies the repo with
shutil.copytree; a sha256 snapshot of the real gate files self-reports in
tearDown if any test mutated the real repo.
"""

from __future__ import annotations

import configparser
import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests._support import REPO_ROOT

GUARDED = (
    "lints/import-linter.toml",
    ".github/workflows/check.yml",
    ".claude-plugin/plugin.json",
    "scripts/examples.json",
    "plugin.json",
)
COPY_IGNORE = shutil.ignore_patterns(".git", "__pycache__", ".ruff_cache", "dist")
SUBPROCESS_TIMEOUT = 300


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_checker(argv, root_arg=None):
    """Run a checker with python3 -I; return (returncode, combined output)."""
    args = ["python3", "-I"] + list(argv)
    if root_arg is not None:
        args.append(str(root_arg))
    proc = subprocess.run(
        args, cwd=str(REPO_ROOT), capture_output=True, text=True,
        timeout=SUBPROCESS_TIMEOUT,
    )
    return proc.returncode, proc.stdout + proc.stderr


class GuardedRepoCase(unittest.TestCase):
    """Snapshot the real gate files; copy the repo for mutation."""

    def setUp(self):
        self._snapshot = {rel: _sha256(REPO_ROOT / rel) for rel in GUARDED}
        self.addCleanup(self._verify_real_repo_untouched)
        self.tmp = Path(tempfile.mkdtemp(prefix="bpy-failpath."))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.copy = self.tmp / "repo"
        shutil.copytree(REPO_ROOT, self.copy, ignore=COPY_IGNORE)
        self.assertFalse((self.copy / ".git").exists(), "copy must not carry .git")

    def _verify_real_repo_untouched(self):
        mutated = [
            rel for rel, digest in self._snapshot.items()
            if not (REPO_ROOT / rel).is_file() or _sha256(REPO_ROOT / rel) != digest
        ]
        self.assertEqual(
            mutated, [],
            "TEST BUG: the real repo's gate files were mutated: %s" % mutated,
        )


class BrokenPythonBlock(GuardedRepoCase):
    """A broken ```python block in a plain doc tree fails check-examples."""

    def test_broken_python_block_fails_check_examples(self):
        md = self.tmp / "README.md"
        md.write_text("# Demo\n\n```python\ndef f(:\n```\n", encoding="utf-8")
        rc, out = run_checker(["scripts/check-examples.py"], root_arg=self.tmp)
        self.assertEqual(rc, 1)
        self.assertIn("README.md", out)


class CopiedRepoFailures(GuardedRepoCase):
    """Failure paths that mutate a full copy of the repo."""

    def test_malformed_harness_list_is_reported_not_crashed(self):
        harness = self.copy / "scripts" / "examples.json"
        harness.write_text('{"files": ["oops"]}', encoding="utf-8")
        rc, out = run_checker(["scripts/check-examples.py"], root_arg=self.copy)
        self.assertEqual(rc, 1)
        self.assertIn("files must be a JSON object", out)

    def test_place_files_escape_is_rejected(self):
        script = sorted(self.copy.glob("skills/*/evals/*/place-files.sh"))[0]
        with script.open("a", encoding="utf-8") as fh:
            fh.write("\ncp files/../../outside.py .\n")
        rc, out = run_checker(["scripts/check-skill.py"], root_arg=self.copy)
        self.assertEqual(rc, 1)
        self.assertIn("escapes files/", out)

    def test_interface_bogus_key_rejected(self):
        manifest = self.copy / "plugin.json"
        data = json.loads(manifest.read_text(encoding="utf-8"))
        data["extensions"]["com.openai"]["interface"]["bogusInterfaceKey"] = "x"
        manifest.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        rc, out = run_checker(["scripts/check-skill.py"], root_arg=self.copy)
        self.assertEqual(rc, 1)
        self.assertIn("is not in the schema", out)

    def test_nested_reference_compiled(self):
        sub = self.copy / "skills" / "python-port" / "references" / "sub"
        sub.mkdir(parents=True, exist_ok=True)
        (sub / "broken.md").write_text(
            "# Nested reference\n\n```python\ndef f(:\n```\n", encoding="utf-8"
        )
        rc, out = run_checker(["scripts/check-examples.py"], root_arg=self.copy)
        self.assertEqual(rc, 1)
        self.assertIn("skills/python-port/references/sub/broken.md", out)


class DeletedContract(GuardedRepoCase):
    """Text-surgery on a copy's import-linter.toml: removing a contract must
    fail the CI validator replica (mirrors the check.yml heredoc verbatim)."""

    def _surgery(self, header):
        path = self.copy / "lints" / "import-linter.toml"
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        idx = [i for i, line in enumerate(lines) if line.strip() == header][0]
        nxt = next(
            (j for j in range(idx + 1, len(lines)) if lines[j].startswith("[")),
            len(lines),
        )
        path.write_text("".join(lines[:idx] + lines[nxt:]), encoding="utf-8")

    def _replica(self, path):
        try:
            cp = configparser.ConfigParser()
            cp.read(path)
            sections = cp.sections()
            assert "importlinter" in sections, "missing [importlinter] root section"
            contracts = [s for s in sections if s.startswith("importlinter:contract:")]
            assert contracts, "no contracts found in lints/import-linter.toml"
            assert any("layers" in s for s in contracts), "layered contract missing"
            assert any("forbidden" in s for s in contracts), "domain-purity contract missing"
            for section in contracts:
                ctype = cp.get(section, "type")
                assert ctype in ("layers", "forbidden", "independence"), (
                    "contract %s has invalid type %s" % (section, ctype)
                )
        except Exception as exc:
            return False, str(exc)
        return True, ""

    def test_deleted_contract_fails_config_root(self):
        self._surgery("[importlinter]")
        ok, message = self._replica(self.copy / "lints" / "import-linter.toml")
        self.assertFalse(ok)
        self.assertIn("missing [importlinter] root section", message)

    def test_deleted_contract_fails_config_layers(self):
        self._surgery("[importlinter:contract:layers]")
        ok, message = self._replica(self.copy / "lints" / "import-linter.toml")
        self.assertFalse(ok)
        self.assertIn("layered contract missing", message)

    def test_deleted_contract_fails_config_forbidden(self):
        self._surgery("[importlinter:contract:domain-purity]")
        ok, message = self._replica(self.copy / "lints" / "import-linter.toml")
        self.assertFalse(ok)
        self.assertIn("domain-purity contract missing", message)


if __name__ == "__main__":
    unittest.main()
