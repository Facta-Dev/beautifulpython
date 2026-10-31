#!/usr/bin/env python3
"""Prove the skill's lints fire: every # expect: rule in lints/check/violations.py
must report on its marked line, nothing else may report, and the selected rules
in lints/ruff.toml must match the violations file's rule list.

Runs ruff with --output-format json. Exit 1 on any failure, 2 if ruff is
unavailable. Stdlib only, Python 3.9+.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

ROOT = Path(__file__).resolve().parents[1]

SELECT_RE = re.compile(r'"([A-Z]\w*\d+)"')
EXPECT_RE = re.compile(r"#\s*expect:\s*([A-Z]\w*\d+(?:,\s*[A-Z]\w*\d+)*)")


def selected_rules(config_path: Path) -> Dict[str, int]:
    """Rule code -> the line of lints/ruff.toml that selects it."""
    rules: Dict[str, int] = {}
    in_select = False
    for number, line in enumerate(config_path.read_text(encoding="utf-8").splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("select"):
            in_select = True
            continue
        if not in_select:
            continue
        if stripped.startswith("]"):
            in_select = False
            continue
        for code in SELECT_RE.findall(line):
            rules.setdefault(code, number)
    return rules


def expects(violations_path: Path) -> List[Tuple[int, Set[str]]]:
    """(1-based line, expected rule codes) for each marked line."""
    found: List[Tuple[int, Set[str]]] = []
    for number, line in enumerate(
        violations_path.read_text(encoding="utf-8").splitlines(), 1
    ):
        match = EXPECT_RE.search(line)
        if match:
            codes = {code.strip() for code in match.group(1).split(",")}
            found.append((number, codes))
    return found


def run_ruff(config: Path, check_dir: Path, ruff: str) -> Tuple[int, Dict[Tuple[int, str], str], str]:
    argv = [
        ruff, "check", "--config", str(config),
        "--output-format", "json", str(check_dir),
    ]
    try:
        result = subprocess.run(
            argv, capture_output=True, text=True, check=False, timeout=120
        )
    except OSError:
        return 127, {}, "ruff binary failed to run"
    except subprocess.TimeoutExpired:
        return 124, {}, "ruff did not finish within 120s"
    fired: Dict[Tuple[int, str], str] = {}
    try:
        msgs = json.loads(result.stdout)
    except ValueError:
        first = (result.stderr.splitlines() or ["(no stderr)"])[0]
        return result.returncode, {}, "ruff output is not JSON: %s" % first
    if isinstance(msgs, dict):
        msgs = [msgs]
    for msg in msgs:
        row = int(msg.get("location", {}).get("row", 0))
        code = str(msg.get("code"))
        if not code or code == "None":
            continue
        message = str(msg.get("message", "")).split("\n")[0]
        # The same violation can be reported once per bad item on one line
        # (two mutable defaults, two flagged names). First report wins.
        fired.setdefault((row, code), message)
    return result.returncode, fired, result.stderr


def check(root: Path, ruff: str) -> Tuple[List[str], int]:
    """Return (problems, number of proven lints)."""
    config = root / "lints" / "ruff.toml"
    check_dir = root / "lints" / "check"
    violations = check_dir / "violations.py"
    problems: List[str] = []
    if not config.is_file():
        problems.append("missing lints/ruff.toml")
        return problems, 0
    if not violations.is_file():
        problems.append("missing lints/check/violations.py")
        return problems, 0
    rules = selected_rules(config)
    if not rules:
        problems.append("lints/ruff.toml: no rules found in the select list")
    expect_list = expects(violations)
    if not expect_list:
        problems.append("lints/check/violations.py: no # expect: markers found")
    expect_codes: Set[str] = set()
    for _, codes in expect_list:
        expect_codes.update(codes)
    for code in sorted(expect_codes - set(rules)):
        problems.append(
            "lints/check/violations.py: expect %s is not selected in lints/ruff.toml" % code
        )
    for code, line in sorted(rules.items()):
        if code not in expect_codes:
            problems.append(
                "lints/ruff.toml:%d: %s is selected but has no violation in "
                "lints/check/violations.py" % (line, code)
            )
    if not problems:
        _, fired, stderr = run_ruff(config, check_dir, ruff)
    else:
        fired, stderr = {}, ""
    matched: Set[Tuple[int, str]] = set()
    proven = 0
    for line, codes in expect_list:
        for code in sorted(codes):
            hits = {c for (row, c) in fired if row == line}
            if code in hits:
                matched.add((line, code))
                proven += 1
            else:
                problems.append(
                    "lints/check/violations.py:%d: expected %s did not fire" % (line, code)
                )
    for (row, code), message in sorted(fired.items()):
        if (row, code) not in matched:
            problems.append(
                "lints/check/violations.py:%d: unexpected %s: %s" % (row, code, message)
            )
    if stderr:
        problems.extend(stderr.splitlines())
    return problems, proven


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Prove every selected ruff rule fires on lints/check/violations.py."
    )
    parser.add_argument("root", nargs="?", default=str(ROOT), help="repository root")
    parser.add_argument("--json", dest="as_json", action="store_true", help="print findings as JSON")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    ruff = shutil.which("ruff")
    if ruff is None:
        sys.stderr.write("check-lints: ruff not found on PATH\n")
        return 2
    problems, proven = check(root, ruff)
    if args.as_json:
        json.dump(
            {"ok": not problems, "problem_count": len(problems), "fired": proven, "problems": problems},
            sys.stdout,
            indent=2,
        )
        sys.stdout.write("\n")
    else:
        for problem in problems:
            sys.stdout.write(problem + "\n")
        if not problems:
            sys.stdout.write("%d expected lints fired; table matches lints/ruff.toml\n" % proven)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
