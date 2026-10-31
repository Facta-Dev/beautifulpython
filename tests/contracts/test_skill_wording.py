#!/usr/bin/env python3
"""Contract tests: SKILL.md wording guarantees (the unbreakable-clause pins).

Read-only pins: if one of these red-fails, someone edited away the unbreakable-
contract language or the cross-skill references — a regression, not style.
"""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BP = REPO_ROOT / "skills" / "python-best-practices" / "SKILL.md"
RV = REPO_ROOT / "skills" / "python-review" / "SKILL.md"


def bp_body() -> str:
    return BP.read_text(encoding="utf-8")


def rv_body() -> str:
    return RV.read_text(encoding="utf-8")


class BestPracticesClause(unittest.TestCase):
    def test_unbreakable_clause_present(self):
        body = bp_body()
        self.assertIn("**unbreakable and non-waivable**", body)
        self.assertIn("never to weaken or delete the contract", body)
        self.assertIn("re-cut the layout", body)

    def test_silencing_prohibition(self):
        body = bp_body()
        self.assertIn("never to silence it with", body)
        for token in ("# noqa", "# type: ignore", "__getattr__"):
            self.assertIn(token, body)

    def test_names_the_mandated_stack(self):
        body = bp_body()
        for token in ("fastapi", "sqlalchemy", "taskiq", "httpx"):
            self.assertIn(
                token, body, "domain I/O-free wall must name %s" % token
            )
        self.assertIn("Dragonfly/Redis", body)

    def test_points_at_review_as_the_critic(self):
        body = bp_body()
        self.assertIn("Review treats a broken contract as an automatic Must fix", body)
        self.assertIn("`python-review`", body)

    def test_domain_import_nothing_bullet(self):
        body = bp_body()
        self.assertIn("Dependencies point inward, only", body)
        self.assertIn("`domain` is I/O-free", body)
        self.assertIn("Slices don't import each other", body)


class ReviewSkillClauses(unittest.TestCase):
    def test_architecture_category_ranks_first_as_must_fix(self):
        body = rv_body()
        self.assertIn("Architecture contracts (always Must fix, ranked first)", body)
        self.assertIn("a broken architecture contract (ranked above everything)", body)

    def test_waiver_detection_clause(self):
        body = rv_body()
        self.assertIn("Waived gates:", body)
        self.assertIn("flag the deletion itself, loudly", body)

    def test_tools_run_contracts_first(self):
        body = rv_body()
        self.assertIn("lint-imports", body)
        self.assertLess(
            body.index("lint-imports"), body.index("ruff check"),
            "lint-imports must be listed before ruff in the tools-first block",
        )

    def test_stack_digest_reference(self):
        body = rv_body()
        self.assertIn("fastapi-taskiq.md", body)


if __name__ == "__main__":
    unittest.main()