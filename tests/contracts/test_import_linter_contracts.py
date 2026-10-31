#!/usr/bin/env python3
"""Contract tests: lints/import-linter.toml — the unbreakable slicing contracts.

Every test here is a guarantee someone must NOT be able to silently remove. Read-only
on the real repo; anything that mutates lives in tests/integration/.
"""

from __future__ import annotations

import configparser
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACTS = REPO_ROOT / "lints" / "import-linter.toml"

LAYERED = "importlinter:contract:layers"
DOMAIN_PURITY = "importlinter:contract:domain-purity"

# The mandated backend stack — the domain ring imports NONE of these.
STACK_MODULES = {
    "fastapi",
    "sqlalchemy",
    "httpx",
    "taskiq",
    "redis",
    "asyncpg",
    "psycopg2",
    "sqlalchemy.ext",
    "redis.asyncio",
}


def load_contracts() -> configparser.ConfigParser:
    cp = configparser.ConfigParser()
    cp.read(CONTRACTS)
    return cp


def raw_text() -> str:
    return CONTRACTS.read_text(encoding="utf-8")


class RootSection(unittest.TestCase):
    def test_root_section_present(self):
        cp = load_contracts()
        self.assertIn("importlinter", cp.sections())
        self.assertEqual(cp.get("importlinter", "root_package"), "<app>")


class LayeredContract(unittest.TestCase):
    def test_layered_present_with_domain_at_bottom(self):
        cp = load_contracts()
        section = "importlinter:contract:layers"
        self.assertIn(section, cp.sections())
        self.assertEqual(cp.get(section, "type"), "layers")
        layers = [x for x in cp.get(section, "layers").splitlines() if x.strip()]
        self.assertEqual(
            layers,
            ["<app>.composition", "<app>.<scope>", "<app>.ports", "<app>.domain"],
            "composition top -> scope -> ports -> domain bottom; order is the law",
        )

    def test_layered_contract_name_states_direction(self):
        cp = load_contracts()
        self.assertIn(
            "point in", cp.get(LAYERED, "name").lower(), "name says dependencies point in"
        )


class DomainPurityContract(unittest.TestCase):
    def test_is_forbidden_type_with_domain_only_source(self):
        cp = load_contracts()
        section = "importlinter:contract:domain-purity"
        self.assertIn(section, cp.sections())
        self.assertEqual(cp.get(section, "type"), "forbidden")
        sources = [x for x in cp.get(section, "source_modules").splitlines() if x.strip()]
        self.assertEqual(sources, ["<app>.domain"])

    def test_forbids_the_whole_mandated_stack(self):
        cp = load_contracts()
        forbidden = {
            x for x in cp.get(DOMAIN_PURITY, "forbidden_modules").splitlines() if x.strip()
        }
        self.assertTrue(
            STACK_MODULES <= forbidden,
            "domain-purity must forbid every mandated stack module; missing: %s"
            % sorted(STACK_MODULES - forbidden),
        )

    def test_forbidden_list_cannot_truncate(self):
        cp = load_contracts()
        body = raw_text()
        self.assertIn(
            "never remove a line", body,
            "file must instruct that no forbidden import line is removable",
        )


class SliceIndependenceSkeleton(unittest.TestCase):
    def test_independence_contract_skeleton_ships_commented(self):
        body = raw_text()
        self.assertIn("importlinter:contract:slice-independence", body)
        self.assertIn("type = independence", body)
        self.assertIn("<app>.<other-scope>", body)
        # It ships DISABLED (commented) because independence needs >= 2 real slices;
        # a commented-out block must not parse as a live section in this drop-in.
        cp = load_contracts()
        self.assertNotIn("importlinter:contract:slice-independence", cp.sections())


class AntiWeakening(unittest.TestCase):
    def test_no_active_contract_is_empty(self):
        cp = load_contracts()
        for section in cp.sections():
            if not section.startswith("importlinter:contract:"):
                continue
            for opt in ("layers", "source_modules", "forbidden_modules"):
                if cp.has_option(section, opt):
                    values = [x for x in cp.get(section, opt).splitlines() if x.strip()]
                    self.assertTrue(values, "%s.%s is empty — weakened contract" % (section, opt))

    def test_header_says_non_waivable(self):
        body = raw_text()
        self.assertIn("weakened, removed, or waived", body)
        self.assertIn("re-cut the layout", body)
        self.assertIn("CI runs `lint-imports` and fails the build", body)


if __name__ == "__main__":
    unittest.main()