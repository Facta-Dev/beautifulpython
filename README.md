# Beautiful Python

Three standard [Agent Skills](https://agentskills.io) and a lints config that teach
coding agents to write, review, port, and enforce idiomatic Python:

- **`python-best-practices`** loads whenever an agent writes or changes Python, and
  steers it toward idiomatic, robust, maintainable code.
- **`python-review`** reviews existing Python code, a file, a module, or a diff, and
  writes a prioritized report where every finding cites the rule it breaks and shows
  the fix.
- **`python-port`** ports C, C++, Rust, Go, Java, JavaScript, or TypeScript to
  idiomatic Python with the same behavior, porting the original tests first so you can
  prove the two match.
- **`lints/`** is a drop-in ruff + mypy configuration that enforces the
  machine-checkable rules in CI.

They work with Claude Code, OpenAI Codex, GitHub Copilot, Cursor, Gemini CLI, and any
other agent that reads the Agent Skills format. Every code example in the skills
compiles on a clean Python interpreter, and every lint in the config was checked
against ruff's current rules.

The guidance is distilled from five sources, with a condensed digest of each bundled in
the skill so the agent can consult the original reasoning when it needs to:

- [PEP 8 — Style Guide for Python Code](https://peps.python.org/pep-0008/) and
  [PEP 20 — The Zen of Python](https://peps.python.org/pep-0020/)
- [PEP 257 — Docstring Conventions](https://peps.python.org/pep-0257/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Effective Python](https://www.effectivepython.com) by Brett Slatkin (3rd edition)
- [The Python typing documentation](https://typing.readthedocs.io)

Where the sources disagree, the skill picks a side and says why.

## What it changes

Asked for a small semver-parsing module, an agent without the skill produced working
code with public mutable fields, exception messages built as return-value contracts,
and error paths the tests never covered. With the skill, the same agent froze the
record with a dataclass, raised a dedicated error carrying the offending value, and
wrote doctest examples users can copy safely. Condensed from those two runs:

```python
# Without the skill
class Version:
    def __init__(self, major, minor, patch, pre=None, build=None):
        self.major = major
        self.minor = minor
        self.patch = patch
        self.pre = pre
        self.build = build

def parse(s):
    assert s, "empty"
    parts = s.split(".")
    return Version(int(parts[0]), int(parts[1]), int(parts[2]))
```

```python
# With the skill
from dataclasses import dataclass

@dataclass(frozen=True)
class Version:
    """A semantic version. Ordering ignores build metadata."""

    major: int
    minor: int
    patch: int
    pre: tuple[str, ...] = ()

    @classmethod
    def parse(cls, text: str) -> "Version":
        msg = f"invalid semver: {text!r}"
        parts = text.split(".")
        if len(parts) != 3:
            raise VersionError(msg)
        try:
            return cls(int(parts[0]), int(parts[1]), int(parts[2]))
        except ValueError as err:
            raise VersionError(msg) from err


class VersionError(ValueError):
    """Raised when a string is not a semver 2.0.0 version."""
```

Across the same test tasks (a library, a messy-module refactor, and a review), the
skill's eval cases grade an agent on exactly these behaviors: see
[Testing the skills](#testing-the-skills).

## Install

Each skill is a folder under `skills/`: `python-best-practices/`, `python-review/`, and
`python-port/`. Every option below puts those folders where your agent looks for
skills. Install all three; the review and port skills lean on the best-practices skill
for style.

### Any agent, one command

The [`skills`](https://github.com/vercel-labs/skills) installer supports most agents
(Node 22.20 or later):

```bash
npx skills add Facta-Dev/beautifulpython
```

Add `-g` to install for your user instead of the current project, or `-a <agent>` to
pick an agent, such as `-a codex` or `-a cursor`.

### Claude Code

Install it as a plugin so updates arrive with one command:

```bash
claude plugin install beautiful-python --marketplace Facta-Dev/beautifulpython
```

Inside a session, the same thing is:

```
/plugin marketplace add Facta-Dev/beautifulpython
/plugin install beautiful-python@beautiful-python
```

This installs all three skills. They appear as `/beautiful-python:python-best-practices`,
`/beautiful-python:python-review`, and `/beautiful-python:python-port`, though you
rarely need to call them, since they trigger on their own. To try it for one session
without installing, clone the repo and run `claude --plugin-dir ./beautifulpython`.

### OpenAI Codex

Install it as a plugin:

```bash
codex plugin marketplace add Facta-Dev/beautifulpython
codex plugin add beautiful-python@beautiful-python
```

This installs all three skills as `beautiful-python:python-best-practices`,
`beautiful-python:python-review`, and `beautiful-python:python-port`. The same package
works in the ChatGPT desktop app.

### GitHub Copilot

With GitHub CLI 2.90 or later:

```bash
gh skill install Facta-Dev/beautifulpython python-best-practices
gh skill install Facta-Dev/beautifulpython python-review
gh skill install Facta-Dev/beautifulpython python-port
```

This installs into the current project by default. Add `--scope user` to install for
your user, or `--agent <name>` to install for a different agent.

### Gemini CLI

```bash
gemini skills install https://github.com/Facta-Dev/beautifulpython --path skills/python-best-practices
gemini skills install https://github.com/Facta-Dev/beautifulpython --path skills/python-review
gemini skills install https://github.com/Facta-Dev/beautifulpython --path skills/python-port
```

### Cursor or anything else: copy the folder

Clone the repo and copy the three skill folders into your agent's skills directory.
Most agents now read the shared `.agents/skills/` location:

```bash
git clone https://github.com/Facta-Dev/beautifulpython
mkdir -p ~/.agents/skills
cp -R beautifulpython/skills/python-* ~/.agents/skills/
```

| Agent | User directory | Project directory |
|---|---|---|
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| OpenAI Codex | `~/.agents/skills/` | `.agents/skills/` |
| GitHub Copilot | `~/.copilot/skills/` or `~/.agents/skills/` | `.github/skills/` or `.agents/skills/` |
| Cursor | `~/.cursor/skills/` or `~/.agents/skills/` | `.cursor/skills/` or `.agents/skills/` |
| Gemini CLI | `~/.gemini/skills/` or `~/.agents/skills/` | `.gemini/skills/` or `.agents/skills/` |

Claude Code does not read `.agents/skills/`, so use its own directory or the plugin.
Restart the agent if the skill doesn't show up right away.

### claude.ai

claude.ai takes one zip per skill, with the skill folder as the zip root:

```bash
cd skills
zip -r ../python-best-practices.zip python-best-practices -x '*.DS_Store' -x '*/evals/*'
zip -r ../python-review.zip python-review -x '*.DS_Store' -x '*/evals/*'
zip -r ../python-port.zip python-port -x '*.DS_Store' -x '*/evals/*'
```

Upload each under **Customize > Skills**. Code execution must be enabled first.

## Reviewing existing code

Ask your agent to review a file, package, or diff, for example "review src/parser.py"
or "what would you change in this PR". The `python-review` skill runs ruff, the
project's type checker, and the tests when tooling is available, then writes a report
with three tiers: must fix, should fix, and consider. Every finding gives a `file:line`
location, the rule it breaks with its source (a PEP, an Effective Python item, a ruff
or mypy rule code), and the smallest code change that fixes it. Each report ends with
what the code already does well.

## Porting code to Python

Ask your agent to port a module, for example "port parser.c to Python" or "rewrite
this Go service in Python". The `python-port` skill reads the original and its tests,
ports the tests first, designs a Python API instead of transliterating the original,
and verifies with pytest, ruff, and mypy. It maps each language's habits to their
Python equivalents: error codes and out-parameters to exceptions carrying the data,
`NULL` to `None` with `| None` in the signature, flag bitmasks to keyword options or
`enum.Flag`, structs to frozen dataclasses, and header files away entirely. Each port
comes with a `PORTING.md` that maps the old API and tests to the new ones and lists
every deliberate difference.

## FastAPI, TaskIQ, and the backend stack

For services on the FastAPI + TaskIQ + Dragonfly (Redis protocol) +
Postgres/pgvector stack with a hexagonal, vertical-slice layout, some general Python
advice is wrong for the framework. Taken at face value, the skills would tell an agent
to hand-build a dependency graph, re-validate what `Path`/`Query`/`Body` already
validated, and make pydantic model fields private. When code imports `fastapi` or
`taskiq`, both the writing and review skills read
[`references/fastapi-taskiq.md`](skills/python-best-practices/references/fastapi-taskiq.md)
first. It covers the stack and does two things:

- **It names the conventions to leave alone:** `Depends`-injected parameters, pydantic
  models keeping public fields, the framework-managed DI graph, and the
  composition-root wiring.
- **It lists the bugs that pass every lint.** Blocking I/O inside `async def` handlers,
  sessions held across awaits on unrelated I/O, task handlers capturing
  request-scoped clients from the web process, Dragonfly keys without TTLs, and
  pgvector queries using a different distance metric than the index.

## Enforcing the rules with ruff

The skills teach the rules; the lints keep them from slipping back in. Copy
[`lints/ruff.toml`](lints/ruff.toml) into your `pyproject.toml` as `[tool.ruff.lint]`
and [`lints/mypy.ini`](lints/mypy.ini) as the `[tool.mypy]` block, then run:

```bash
ruff check --exit-code .
mypy .
```

It flags bare `assert` outside tests, mutable default arguments, exceptions raised
with inline string literals, imports below the top level, wildcard imports, `== True`
comparisons, `print()` in library code, bare `except:`, raises without `from` inside
`except`, `noqa` without a firing rule, and more. The config is a focused allowlist:
every rule is proven to fire.

Every rule in the table is proven to fire. [`lints/check/violations.py`](lints/check/violations.py)
is a small module with one deliberate violation per rule, and this script runs ruff on
it from the repo root:

```bash
pip install ruff          # once, or use uv/pipx
python3 scripts/check-lints.py
```

It fails if a rule stops firing, if something unexpected fires, or if the select table
drifts from the violations file.

## What the writing skill covers

`skills/python-best-practices/SKILL.md` is about 350 lines, organized so an agent can
scan it while coding:

1. Mindset: Python-shaped code, EAFP, application vs library
2. Before you hand back code: ruff, the type checker, tests; lint policy
3. Data modeling: dataclasses before dicts, frozen by default, no bool params
4. Types: annotations, protocols, validate-once-at-the-boundary
5. Errors and failures: narrow exceptions, chaining, no swallowing
6. Everyday idioms: comprehensions, enumerate/zip, f-strings, pathlib
7. Imports, modules, and packages
8. Concurrency and async
9. Packaging, dependencies, and tooling
10. Documentation and docstrings
11. Tests
12. Performance, in order
13. Final checklist

`skills/python-best-practices/references/` holds one digest per source for deeper
lookups, plus the stack reference for FastAPI and TaskIQ code.

## Layout

```
beautifulpython/
├── .claude-plugin/
│   ├── plugin.json         Claude Code plugin manifest
│   └── marketplace.json    lets this repo act as its own marketplace
├── .agents/plugins/
│   └── marketplace.json    the same, for Codex
├── plugin.json             Codex and ChatGPT plugin manifest
├── assets/icon.png         plugin icon for Codex and ChatGPT
├── skills/
│   ├── python-best-practices/   writing skill
│   │   ├── SKILL.md
│   │   ├── references/          one digest per source, plus fastapi-taskiq.md
│   │   └── evals/
│   ├── python-review/           review skill
│   │   ├── SKILL.md
│   │   └── evals/
│   └── python-port/             porting skill
│       ├── SKILL.md
│       └── evals/               a C module to port, with its tests
├── lints/
│   ├── ruff.toml                the drop-in ruff config
│   ├── mypy.ini                 the drop-in mypy config
│   └── check/                   one deliberate violation per rule
├── scripts/
│   ├── check-skill.py           validates skills, evals, and manifests
│   ├── check-lints.py           proves every selected rule fires
│   ├── check-examples.py        compiles every Python example in the docs
│   ├── examples.json            context that lets fragment examples compile
│   └── package-openai-plugin.py builds the ChatGPT / Codex directory ZIP
├── tests/
│   └── test_*.py                the checker, harness, and packager test suites
├── CHANGELOG.md
├── CONTRIBUTING.md
├── PRIVACY.md
└── README.md
```

## Testing the skills

`skills/python-best-practices/evals/` holds two test cases in the layout `claude plugin
eval` reads: a library API design task (a semver parser) and a refactor-this-module
task with an input file. Each case has the prompt, a description of a good result, and
one assertion per file under `graders/`. Run them with and without the skill from the
skill directory:

```bash
claude plugin eval . --allow-tools Write,Edit,Bash --scaffold
```

`skills/python-review/evals/` holds a review case for the same messy module, and
`skills/python-port/evals/` holds a C module to port with its original test suite.
Run them the same way from each skill's directory.

These are real model runs and are billed.

## Updating

Edit the skill, bump `version` in both `.claude-plugin/plugin.json` and `plugin.json`
(the checker fails if they differ), commit, and push. Claude Code plugin users pick up
the new version with:

```bash
claude plugin update beautiful-python
```

Codex users refresh the marketplace with:

```bash
codex plugin marketplace upgrade beautiful-python
```

Anyone who copied the folder or used an installer re-runs the install command. Record
each release in [CHANGELOG.md](CHANGELOG.md).

Validate before pushing.

```bash
python3 -I scripts/check-skill.py                 # skills, evals, manifests
python3 -I scripts/check-examples.py              # compile every Python example
python3 -I scripts/check-lints.py                 # needs ruff on PATH
python3 -I -m unittest discover -s tests -t .     # the checker's own tests
claude plugin validate .
```

Pass `--json` to the first two scripts for machine-readable output.

To publish a release to the ChatGPT / Codex Plugins Directory, update `release_notes`
in `plugin.json`, then build the upload:

```bash
python3 scripts/package-openai-plugin.py
```

This writes `dist/beautiful-python-<version>.zip` with the manifest, the skills and
their references, the icon, the license, and the privacy policy, but not the eval
cases. Upload it at [platform.openai.com/plugins](https://platform.openai.com/plugins)
from a verified developer account, as described in OpenAI's
[submission guide](https://developers.openai.com/plugins/deploy/submission).

## Contributing

Issues and pull requests are welcome. Every rule needs a published source; see
[CONTRIBUTING.md](CONTRIBUTING.md) for how to propose a rule, report a review false
positive, or add an eval case.

## Sources and attribution

The guidance in this skill is a synthesis. The digests in
`skills/python-best-practices/references/` are paraphrased summaries written for this
project; they restate each source's advice in condensed form and link back to the
original. Read the originals for the full reasoning.

| Source | Author | License |
|---|---|---|
| [PEP 8](https://peps.python.org/pep-0008/) and [PEP 20](https://peps.python.org/pep-0020/) | Guido van Rossum, Barry Warsaw, et al. | PSF / public domain |
| [PEP 257](https://peps.python.org/pep-0257/) | David Goodger, Guido van Rossum | public domain |
| [Python typing documentation](https://typing.readthedocs.io) | The typing council and contributors | CC BY (docs spec) |
| [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) | Google | CC BY 3.0 |
| [Effective Python](https://www.effectivepython.com) | Brett Slatkin, published by Addison-Wesley | all rights reserved (digest paraphrases) |

The skill text, the digests, the icon, and the checker scripts in this repository are
MIT licensed (see [LICENSE](LICENSE)).

The repo is a sibling of [BeautifulRust](https://github.com/morganlinton/BeautifulRust),
which holds the Rust half of this port and the shape this project follows.

## License

MIT. See [LICENSE](LICENSE).
