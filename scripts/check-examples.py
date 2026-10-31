#!/usr/bin/env python3
"""Check that every Python code block in the skills and docs compiles.

Python needs less scaffolding than a compile-to-machine-code language: any
syntactically valid fragment statement, function, or class compiles on its own,
so most blocks run with no context. scripts/examples.json still exists for the
blocks that need it (a per-file prelude, a per-block template) and for skips
with a reason. Run with python3 -I.

py_compile proves syntax; it does not execute anything. ruff and mypy prove the
rest of what a compiler would catch in a statically typed language.

Stdlib only, Python 3.9+. Exit 1 on any error.
"""

from __future__ import annotations

import argparse
import json
import py_compile
import re
import sys
import tempfile
import textwrap
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

HARNESS = Path("scripts") / "examples.json"
DOC_GLOBS = (
    "README.md",
    "CONTRIBUTING.md",
    "examples/*.md",
    "skills/*/SKILL.md",
    "skills/*/references/*.md",
)
FENCE_RE = re.compile(r"^(\s*)(`{3,}|~{3,})\s*([^`\s]*)")
CODE = "{code}"


@dataclass(frozen=True)
class Problem:
    path: str
    line: int
    level: str
    message: str


@dataclass
class Block:
    path: str
    line: int  # line of the first code line in the markdown file
    index: int  # 1-based position among the file's python blocks
    code: str
    skip: Optional[str] = None
    prelude: str = ""
    template: str = CODE
    lines: Dict[int, Tuple[str, int]] = field(default_factory=dict)


def rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def format_problem(problem: Problem) -> str:
    prefix = "warning: " if problem.level == "warning" else ""
    return "%s:%d: %s%s" % (problem.path, problem.line, prefix, problem.message)


def summary_line(problems: Sequence[Problem], checked: int, skipped: int) -> str:
    errors = sum(1 for p in problems if p.level == "error")
    err_word = "error" if errors == 1 else "errors"
    return "%d %s, %d blocks compiled, %d skipped" % (errors, err_word, checked, skipped)


def doc_files(root: Path) -> List[Path]:
    found = set()
    for pattern in DOC_GLOBS:
        for path in root.glob(pattern):
            if path.is_file() and "evals" not in path.parts:
                found.add(path)
    return sorted(found)


def find_blocks(root: Path, path: Path) -> List[Block]:
    """Return the ```python blocks in one markdown file."""
    blocks: List[Block] = []
    lines = path.read_text(encoding="utf-8").split("\n")
    fence: Optional[str] = None
    is_python = False
    start = 0
    body: List[str] = []
    for number, text in enumerate(lines, 1):
        match = FENCE_RE.match(text)
        if fence is None:
            if match:
                fence = match.group(2)
                lang = match.group(3).split(",")[0]
                is_python = lang in ("python", "py")
                start = number + 1
                body = []
            continue
        if (
            match
            and match.group(2).startswith(fence[0])
            and len(match.group(2)) >= len(fence)
            and not match.group(3)
        ):
            if is_python:
                blocks.append(
                    Block(
                        path=rel(root, path),
                        line=start,
                        index=len(blocks) + 1,
                        code=textwrap.dedent("\n".join(body)),
                    )
                )
            fence = None
            continue
        body.append(text)
    return blocks


def as_text(value: Any) -> str:
    if isinstance(value, list):
        return "\n".join(str(v) for v in value)
    return str(value or "")


def first_code_line(code: str) -> str:
    for text in code.split("\n"):
        if text.strip():
            return text.strip()
    return ""


def apply_harness(root: Path, blocks: List[Block], harness: Dict[str, Any]) -> List[Problem]:
    """Attach preludes, templates, and skips. Report harness drift."""
    problems: List[Problem] = []
    files = harness.get("files", {})
    by_path: Dict[str, List[Block]] = {}
    for block in blocks:
        by_path.setdefault(block.path, []).append(block)
    harness_path = HARNESS.as_posix()
    for path, entry in files.items():
        if path not in by_path:
            problems.append(
                Problem(
                    harness_path, 1, "error",
                    "%s: file has no python blocks or does not exist" % path,
                )
            )
            continue
        for key, spec in (entry.get("blocks") or {}).items():
            try:
                index = int(key)
            except ValueError:
                problems.append(
                    Problem(harness_path, 1, "error", "%s: block key %r is not a number" % (path, key))
                )
                continue
            if index < 1 or index > len(by_path[path]):
                problems.append(
                    Problem(
                        harness_path, 1, "error",
                        "%s: no python block #%d (file has %d)" % (path, index, len(by_path[path])),
                    )
                )
                continue
            block = by_path[path][index - 1]
            expected = (spec.get("first_line") or "").strip()
            actual = first_code_line(block.code)
            if expected != actual:
                problems.append(
                    Problem(
                        block.path, block.line, "error",
                        "python block #%d does not match %s (expected first line %r, found %r); "
                        "blocks were added, moved, or edited, so update the harness"
                        % (index, harness_path, expected, actual),
                    )
                )
                block.skip = "harness out of date"
                continue
            if "skip" in spec:
                reason = str(spec.get("skip") or "").strip()
                if not reason:
                    problems.append(
                        Problem(block.path, block.line, "error", "python block #%d: skip needs a reason" % index)
                    )
                block.skip = reason or "no reason"
                continue
            template = as_text(spec.get("template")) or CODE
            if CODE not in template:
                problems.append(
                    Problem(harness_path, 1, "error", "%s block #%d: template has no {code}" % (path, index))
                )
                template = CODE
            block.template = template
        prelude = as_text(entry.get("prelude"))
        for block in by_path[path]:
            block.prelude = prelude
    return problems


def render(block: Block, harness_label: str) -> str:
    """Build one module's source and record where each line came from."""
    out: List[str] = []
    origin: List[Tuple[str, int]] = []

    def add(text: str, where: Tuple[str, int]) -> None:
        for piece in text.split("\n"):
            out.append(piece)
            origin.append(where)

    if block.prelude:
        add(block.prelude, (harness_label, 1))
    before, _, after = block.template.partition(CODE)
    indent = ""
    if before:
        head = before.rstrip("\n")
        for piece in head.split("\n")[:-1]:
            add(piece, (harness_label, 1))
        indent = head.split("\n")[-1]
        if indent.strip():
            add(indent, (harness_label, 1))
            indent = ""
    for offset, piece in enumerate(block.code.split("\n")):
        line = indent + piece if indent and piece else piece
        out.append(line)
        origin.append((block.path, block.line + offset))
    if after:
        add(after.lstrip("\n"), (harness_label, 1))
    block.lines = {number: where for number, where in enumerate(origin, 1)}
    return "\n".join(out) + "\n"


ERROR_LOCATION_RE = re.compile(r'File "([^"]+)", line (\d+)')


def compile_blocks(to_check: List[Block], tmp: Path) -> List[Problem]:
    """Syntax-check every block as its own module and map errors to markdown lines."""
    modules: Dict[str, Block] = {}
    root = tmp / "examples_check"
    root.mkdir(parents=True)
    for number, block in enumerate(to_check, 1):
        name = "ex_%03d.py" % number
        module = root / name
        module.write_text(render(block, HARNESS.as_posix()), encoding="utf-8")
        modules[module.name] = block
    problems: List[Problem] = []
    seen = set()
    for name, block in modules.items():
        module = root / name
        try:
            py_compile.compile(str(module), doraise=True)
            continue
        except py_compile.PyCompileError as exc:
            chunks = str(exc).strip().splitlines()
            text = "compile failed"
            line_no = 1
            for chunk in chunks:
                match = ERROR_LOCATION_RE.search(chunk)
                if match:
                    line_no = int(match.group(2))
            for chunk in chunks:
                if "Error" in chunk:
                    text = chunk
                    break
            text = text.strip() or "compile failed"
            where = block.lines.get(line_no, (block.path, block.line))
            problem_path, problem_line = where
            label = text
            if where[0] != block.path:
                label = "%s (in the harness code for %s python block #%d)" % (
                    text, block.path, block.index,
                )
            key = (problem_path, problem_line, label)
            if key in seen:
                continue
            seen.add(key)
            problems.append(Problem(problem_path, problem_line, "error", label))
    return problems


def load_harness(root: Path) -> Tuple[Dict[str, Any], List[Problem]]:
    path = root / HARNESS
    if not path.exists():
        return {}, []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        return {}, [Problem(HARNESS.as_posix(), getattr(exc, "lineno", 1), "error", "invalid JSON: %s" % exc)]
    if not isinstance(data, dict):
        return {}, [Problem(HARNESS.as_posix(), 1, "error", "top level must be an object")]
    return data, []


def check_repo(root: Path) -> Tuple[List[Problem], int, int]:
    """Return (problems, compiled block count, skipped block count)."""
    root = Path(root)
    harness, problems = load_harness(root)
    blocks: List[Block] = []
    for path in doc_files(root):
        blocks.extend(find_blocks(root, path))
    if harness:
        problems.extend(apply_harness(root, blocks, harness))
    to_check = [b for b in blocks if b.skip is None]
    skipped = len(blocks) - len(to_check)
    if not to_check:
        return problems, 0, skipped
    with tempfile.TemporaryDirectory(prefix="examples-check.") as tmp:
        found = compile_blocks(to_check, Path(tmp))
    problems.extend(found)
    return problems, len(to_check), skipped


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check that every Python code block in the skills and docs compiles."
    )
    parser.add_argument(
        "root", nargs="?", default=".", help="repository root (default: current directory)"
    )
    parser.add_argument(
        "--json", dest="as_json", action="store_true", help="print findings as JSON"
    )
    args = parser.parse_args(argv)
    problems, checked, skipped = check_repo(Path(args.root))
    errors = sum(1 for p in problems if p.level == "error")
    if args.as_json:
        json.dump(
            {
                "ok": errors == 0,
                "error_count": errors,
                "compiled": checked,
                "skipped": skipped,
                "summary": summary_line(problems, checked, skipped),
                "problems": [asdict(p) for p in problems],
            },
            sys.stdout,
            indent=2,
        )
        sys.stdout.write("\n")
    else:
        for problem in problems:
            sys.stdout.write(format_problem(problem) + "\n")
        sys.stdout.write(summary_line(problems, checked, skipped) + "\n")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
