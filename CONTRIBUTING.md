# Contributing

Issues and pull requests are welcome. The rules here follow one hard constraint and a
few process habits.

## Every rule has a published source

A new rule enters `skills/python-best-practices/SKILL.md` only with a citable source: a
PEP, the Google Python Style Guide, an Effective Python item, the typing docs, or a
documented ecosystem convention. The digests in `skills/python-best-practices/references/`
summarize the sources; keep them in sync when a rule changes. Where sources disagree,
the SKILL.md takes a side and says why in the text.

## Proposing a rule

Open an issue with:

- The rule, stated as guidance an agent can follow while writing code.
- The source and where it appears.
- A before/after Python example.
- Whether ruff, mypy, or any other tool can check it. Machine-checkable rules should
  also get a line in `lints/ruff.toml`, a violation in `lints/check/violations.py`
  (with its `# expect:` marker), and their absence of drift verified by
  `python3 scripts/check-lints.py`.

## Reporting a review false positive

The `python-review` skill may flag code that the author intended. Open an issue with
the snippet, the finding, and why it was deliberate. If the review skill needs a carve
out, add it there and, when it is framework-shaped, in
`skills/python-best-practices/references/fastapi-taskiq.md`.

## Adding an eval case

Eval cases live in the `claude plugin eval` layout: `case.yaml`, `prompt.md`,
`graders/NN-slug.md` per assertion, plus `files/` and a `place-files.sh` when the case
needs input files. Copy an existing case and adapt. The checker
(`python3 -I scripts/check-skill.py`) validates the layout: contiguous grader numbers,
frontmatter on each file, and `place-files.sh` references that resolve.

## Validating changes

```bash
python3 -I scripts/check-skill.py
python3 -I scripts/check-examples.py            # needs no tooling
python3 -I scripts/check-lints.py               # needs ruff on PATH
python3 -I -m unittest discover -s tests        # stdlib unittest; pytest also works
```

All four must pass before a push. Bump `version` in both plugin manifests for any
content change and record the release in [CHANGELOG.md](CHANGELOG.md).
