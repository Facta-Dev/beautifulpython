#!/usr/bin/env python3
"""Tests for scripts/check-examples.py."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests._support import load_script, write

ce = load_script("check-examples.py")


README = """\
# Demo

```python
def double(x: int) -> int:
    return x * 2
```

```bash
ruff check .
```

- A list item with an indented example:

  ```python
  y = double(2)
  ```

~~~markdown
```python
<a template placeholder, not real code>
```
~~~
"""


class RepoTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        write(self.root / "README.md", README)

    def tearDown(self):
        self._tmp.cleanup()

    def blocks(self):
        return ce.find_blocks(self.root, self.root / "README.md")

    def harness(self, data):
        write(self.root / "scripts" / "examples.json", json.dumps(data))


class FindBlocksTest(RepoTest):
    def test_finds_python_blocks_only(self):
        blocks = self.blocks()
        self.assertEqual([b.index for b in blocks], [1, 2])
        self.assertEqual(blocks[0].line, 4)
        self.assertIn("def double", blocks[0].code)

    def test_dedents_indented_blocks(self):
        self.assertEqual(self.blocks()[1].code, "y = double(2);".replace(";", ""))

    def test_ignores_python_fences_nested_in_other_blocks(self):
        codes = " ".join(b.code for b in self.blocks())
        self.assertNotIn("template placeholder", codes)

    def test_skips_eval_fixtures(self):
        write(self.root / "skills" / "demo" / "SKILL.md", "```python\nx = 1\n```\n")
        write(self.root / "skills" / "demo" / "evals" / "case" / "prompt.md", "```python\nbroken\n```\n")
        names = [p.relative_to(self.root).as_posix() for p in ce.doc_files(self.root)]
        self.assertIn("skills/demo/SKILL.md", names)
        self.assertNotIn("skills/demo/evals/case/prompt.md", names)


class HarnessTest(RepoTest):
    def apply(self, data):
        blocks = self.blocks()
        problems = ce.apply_harness(self.root, blocks, data)
        return blocks, problems

    def test_template_and_prelude_are_attached(self):
        blocks, problems = self.apply({"files": {"README.md": {
            "prelude": "from dataclasses import dataclass",
            "blocks": {"2": {"first_line": "y = double(2)",
                             "template": ["def wrap():", "    {code}", "    return y"]}},
        }}})
        self.assertEqual(problems, [])
        self.assertEqual(blocks[0].prelude, "from dataclasses import dataclass")
        self.assertEqual(blocks[1].template, "def wrap():\n    {code}\n    return y")

    def test_first_line_mismatch_reports_drift_at_the_block(self):
        blocks, problems = self.apply({"files": {"README.md": {
            "blocks": {"2": {"first_line": "y = 3", "template": "{code}"}},
        }}})
        self.assertEqual(len(problems), 1)
        self.assertEqual((problems[0].path, problems[0].line), ("README.md", 15))
        self.assertIn("update the harness", problems[0].message)
        self.assertIsNotNone(blocks[1].skip)

    def test_skip_needs_a_reason(self):
        blocks, problems = self.apply({"files": {"README.md": {
            "blocks": {"2": {"first_line": "y = double(2)", "skip": ""}},
        }}})
        self.assertEqual(len(problems), 1)
        self.assertIn("skip needs a reason", problems[0].message)

    def test_skip_with_reason_is_not_an_error(self):
        blocks, problems = self.apply({"files": {"README.md": {
            "blocks": {"2": {"first_line": "y = double(2)", "skip": "a fragment"}},
        }}})
        self.assertEqual(problems, [])
        self.assertEqual(blocks[1].skip, "a fragment")

    def test_unknown_block_and_file_are_errors(self):
        _, problems = self.apply({"files": {
            "README.md": {"blocks": {"9": {"first_line": "x"}}},
            "missing.md": {"blocks": {}},
        }})
        messages = " ".join(p.message for p in problems)
        self.assertIn("no python block #9", messages)
        self.assertIn("missing.md", messages)

    def test_template_without_code_slot_is_an_error(self):
        _, problems = self.apply({"files": {"README.md": {
            "blocks": {"1": {"first_line": "def double(x: int) -> int:", "template": "def f(): pass"}},
        }}})
        self.assertIn("has no {code}", problems[0].message)


class MappingTest(RepoTest):
    def test_rendered_lines_map_back_to_markdown_and_harness(self):
        block = self.blocks()[1]
        block.template = "def wrap():\n    {code}\n    return y"
        source = ce.render(block, "scripts/examples.json").split("\n")
        code_line = source.index([ln for ln in source if ln.endswith("y = double(2)")][0]) + 1
        self.assertEqual(block.lines[code_line], ("README.md", 15))
        self.assertEqual(block.lines[code_line - 1][0], "scripts/examples.json")

    def test_render_records_every_line_origin(self):
        block = self.blocks()[0]
        ce.render(block, "scripts/examples.json")
        self.assertTrue(block.lines)
        self.assertTrue(all(isinstance(v[1], int) for v in block.lines.values()))


class EndToEndTest(RepoTest):
    def test_a_broken_example_reports_its_markdown_line(self):
        write(self.root / "README.md", "# Demo\n\n```python\ndef f():\n    return 1 +\n```\n")
        problems, compiled, skipped = ce.check_repo(self.root)
        self.assertEqual((compiled, skipped), (1, 0))
        self.assertEqual(len(problems), 1)
        self.assertEqual((problems[0].path, problems[0].line), ("README.md", 5))

    def test_a_fragment_compiles_with_its_template(self):
        # Each block is its own module, so block 2 cannot call block 1's double().
        write(self.root / "README.md", README.replace("y = double(2)", "y = 2 * 2"))
        self.harness({"files": {"README.md": {"blocks": {
            "2": {"first_line": "y = 2 * 2", "template": ["def wrap():", "    {code}", "    return y"]},
        }}}})
        problems, compiled, skipped = ce.check_repo(self.root)
        self.assertEqual(problems, [])
        self.assertEqual((compiled, skipped), (2, 0))


if __name__ == "__main__":
    unittest.main()