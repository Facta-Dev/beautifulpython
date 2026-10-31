#!/usr/bin/env python3
"""E2E: run the CI entrypoints exactly as the workflow would, against the real
repo. cwd=REPO_ROOT, python3, timeout=300 on every subprocess. The unittest
gate intentionally discovers only tests/unit so it can never recurse into this
suite; the full tests/ recursion is the CI job itself.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import unittest

from tests._support import REPO_ROOT

SUBPROCESS_TIMEOUT = 300
# Scoped to tests/unit so the gate cannot recurse into this suite.
GATE_ARGS = "-I -m unittest discover -s tests/unit -t ."


def run_ci(argv):
    return subprocess.run(
        ["python3"] + argv,
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=SUBPROCESS_TIMEOUT,
    )


class CiJobs(unittest.TestCase):
    def test_check_skill_job_green(self):
        proc = run_ci(["-I", "scripts/check-skill.py"])
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("0 errors", proc.stdout)

    def test_examples_job_green_with_json_payload(self):
        proc = run_ci(["-I", "scripts/check-examples.py", "--json"])
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertTrue(payload.get("ok"), payload.get("summary"))
        self.assertEqual(payload.get("error_count"), 0)

    @unittest.skipUnless(shutil.which("ruff"), "ruff missing")
    def test_lints_job_green(self):
        # CI installs ruff and runs this without -I, so the e2e mirrors that.
        proc = run_ci(["scripts/check-lints.py"])
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_unittest_gate_green(self):
        proc = run_ci(GATE_ARGS.split())
        self.assertEqual(proc.returncode, 0, proc.stderr)


if __name__ == "__main__":
    unittest.main()
