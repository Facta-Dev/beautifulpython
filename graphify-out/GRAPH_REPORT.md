# Graph Report - .  (2026-11-22)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 958 nodes · 1286 edges · 157 communities (120 shown, 37 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 23 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `da6cca8e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Path
- Beautiful Python
- load_script
- CheckSkillTests
- interface
- What You Must Do When Invoked
- HarnessTest
- test_checker_failure_paths.py
- check-examples.py
- test_ci_gates.py
- config_parse
- load_contracts
- Python best practices
- violations.py
- inventory.py
- inventory.py
- Python review: <what was reviewed>
- BestPracticesClause
- Google Python Style Guide (digest)
- Python port
- check
- Python typing documentation (digest)
- graphify reference: extra exports and benchmark
- PEP 257 (digest)
- PEP 8 (digest, with PEP 20)
- _load
- Effective Python (digest)
- <app> API Designer
- <app> Migration Reviewer
- <app> Ownership Reviewer
- <app> Architect Agent
- <app> Build Resolver Agent
- <app> Code Explorer Agent
- <app> Code Reviewer Agent
- <app> Planner Agent
- <app> TDD Guide Agent
- <app> Depguard Reviewer
- <app> Test Author
- <app> Add Handler
- <app> Add Module
- <app> Claim Check skill
- <app> Clean-Room Rebuild skill
- <app> Corpus Retrieval skill
- <app> Depguard Guard
- <app> Diagnosing Bugs skill
- <app> Domain Modeling skill
- <app> Grilling skill
- <app> learn skill
- <app> Ownership Author
- <app> plan skill
- <app> Research skill
- <app> review skill
- <app> ship skill
- <app> spec skill
- <app> TDD skill
- <app> Verified Status skill
- graphify reference: query, path, explain
- build
- beautifulpython — agent instructions
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- guard-bash.sh
- /add-handler
- /add-module
- /claim-check
- /clean-room-rebuild
- /corpus-retrieval
- /depguard-guard
- /diagnosing-bugs
- /domain-modeling
- /grilling
- /learn
- /ownership-author
- /plan
- /research
- /review
- /ship
- /spec
- /tdd
- /verified-status
- Playbooks for `beautifulpython` — load on demand
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- CLAUDE.md
- README.md
- CREDITS.md
- CREDITS.md
- CREDITS.md
- CREDITS.md
- CREDITS.md
- extraction-spec.md
- CREDITS.md
- CREDITS.md
- CREDITS.md
- CREDITS.md
- __init__.py
- place-files.sh
- place-files.sh
- place-files.sh

## God Nodes (most connected - your core abstractions)
1. `CheckSkillTests` - 35 edges
2. `build_valid_repo()` - 32 edges
3. `write()` - 31 edges
4. `Checker` - 26 edges
5. `Beautiful Python` - 19 edges
6. `Python best practices` - 17 edges
7. `YamlParser` - 16 edges
8. `interface` - 14 edges
9. `config_parse()` - 14 edges
10. `load_script()` - 12 edges

## Surprising Connections (you probably didn't know these)
- `test_basic()` --calls--> `config_parse()`  [INFERRED]
  skills/python-port/evals/port-c-config-parser/files/test_config.c → skills/python-port/evals/port-c-config-parser/files/config.c
- `test_case_insensitive()` --calls--> `config_parse()`  [INFERRED]
  skills/python-port/evals/port-c-config-parser/files/test_config.c → skills/python-port/evals/port-c-config-parser/files/config.c
- `test_duplicates()` --calls--> `config_parse()`  [INFERRED]
  skills/python-port/evals/port-c-config-parser/files/test_config.c → skills/python-port/evals/port-c-config-parser/files/config.c
- `test_empty_input()` --calls--> `config_parse()`  [INFERRED]
  skills/python-port/evals/port-c-config-parser/files/test_config.c → skills/python-port/evals/port-c-config-parser/files/config.c
- `test_get_int_errors()` --calls--> `config_parse()`  [INFERRED]
  skills/python-port/evals/port-c-config-parser/files/test_config.c → skills/python-port/evals/port-c-config-parser/files/config.c

## Import Cycles
- None detected.

## Communities (157 total, 37 thin omitted)

### Community 0 - "Path"
Cohesion: 0.11
Nodes (25): check_repo(), Checker, _fold_block(), format_problem(), _is_relative(), _json_key_line(), main(), _normalize_url() (+17 more)

### Community 1 - "Beautiful Python"
Cohesion: 0.04
Nodes (42): [0.1.0] - 2026-10-30, Changelog, [Unreleased], Adding an eval case, Contributing, Every rule has a published source, Proposing a rule, Reporting a review false positive (+34 more)

### Community 2 - "load_script"
Cohesion: 0.07
Nodes (16): ledger_data(), ledger_paths(), ledger_skip_count(), LedgerAgrees, LedgerShape, path -> the file entry, only for entries that are objects., Number of block specs that ledger a skip (the checker must match it)., The checker's skipped count must equal the ledger's skip count. (+8 more)

### Community 3 - "CheckSkillTests"
Cohesion: 0.18
Nodes (9): write(), add_portable_plugin(), build_valid_repo(), CheckSkillTests, error_messages(), formatted(), png_header(), portable_with() (+1 more)

### Community 4 - "interface"
Cohesion: 0.07
Nodes (29): author, name, url, interface, publication, description, extensions, com.openai (+21 more)

### Community 5 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 6 - "HarnessTest"
Cohesion: 0.14
Nodes (5): EndToEndTest, FindBlocksTest, HarnessTest, MappingTest, RepoTest

### Community 7 - "test_checker_failure_paths.py"
Cohesion: 0.14
Nodes (11): BrokenPythonBlock, CopiedRepoFailures, DeletedContract, GuardedRepoCase, Text-surgery on a copy's import-linter.toml: removing a contract must     fail t, Run a checker with python3 -I; return (returncode, combined output)., Snapshot the real gate files; copy the repo for mutation., A broken ```python block in a plain doc tree fails check-examples. (+3 more)

### Community 8 - "check-examples.py"
Cohesion: 0.21
Nodes (22): apply_harness(), as_text(), Block, check_repo(), compile_blocks(), doc_files(), find_blocks(), first_code_line() (+14 more)

### Community 9 - "test_ci_gates.py"
Cohesion: 0.12
Nodes (11): CheckerSteps, ImportLinterValidator, The unittest gate, scoped so it can never recurse into the e2e suite., Mirror the CI validator body's strengthened assertions against a config;     pre, Every CI job (check, lints, examples) keeps its exact entrypoint., The import-linter config gate: step exists, body pins, replica passes., lints/ruff.toml's select list and violations.py's expect markers pair., RuffPairing (+3 more)

### Community 10 - "config_parse"
Cohesion: 0.28
Nodes (19): config_t, config_count(), config_free(), config_get(), config_get_int(), config_parse(), dup_range(), fail() (+11 more)

### Community 11 - "load_contracts"
Cohesion: 0.19
Nodes (8): ConfigParser, AntiWeakening, DomainPurityContract, LayeredContract, load_contracts(), raw_text(), RootSection, SliceIndependenceSkeleton

### Community 12 - "Python best practices"
Cohesion: 0.11
Nodes (17): 10. Documentation and docstrings, 11. Tests, 12. Performance, in order, 1. Mindset, 2. Before you hand back code, 3. Data modeling, 4. Types, 5. Errors and failures (+9 more)

### Community 13 - "violations.py"
Cohesion: 0.12
Nodes (5): fstring_message(), LegacyBase, One deliberate violation per lint in lints/ruff.toml.  Each expect marker says w, The f-string belongs on its own variable, not inline in the raise., object

### Community 14 - "inventory.py"
Cohesion: 0.18
Nodes (8): add_item(), InventoryError, Item, load(), parse_line(), Exception, Serialize item names to JSON., to_json()

### Community 15 - "inventory.py"
Cohesion: 0.18
Nodes (8): add_item(), InventoryError, Item, load(), parse_line(), Exception, Serialize item names to JSON., to_json()

### Community 16 - "Python review: <what was reviewed>"
Cohesion: 0.13
Nodes (14): 1. Decide the scope, 1. <Short title> (`src/file.py:42`), 2. ..., 2. Run the tools first, if you can, 3. ..., 3. What to look for, in priority order, 4. Write the report, 5. Offer the lints (+6 more)

### Community 17 - "BestPracticesClause"
Cohesion: 0.24
Nodes (4): BestPracticesClause, bp_body(), ReviewSkillClauses, rv_body()

### Community 18 - "Google Python Style Guide (digest)"
Cohesion: 0.17
Nodes (11): Background and goals, Classes, Exceptions, Functions, Google Python Style Guide (digest), Modules and imports, Rules worth flagging as Google-specific, Strings, files, and processes (+3 more)

### Community 19 - "Python port"
Cohesion: 0.18
Nodes (10): 1. Understand the original before writing anything, 2. Port the tests first, 3. Design the Python API, then implement it, 4. Keep the port proportionate, 5. Verify, 6. Write the porting notes, From C and C++, From Go, Java, and JavaScript (+2 more)

### Community 20 - "check"
Cohesion: 0.38
Nodes (9): check(), expects(), main(), Path, Rule code -> the line of lints/ruff.toml that selects it., (1-based line, expected rule codes) for each marked line., Return (problems, number of proven lints)., run_ruff() (+1 more)

### Community 21 - "Python typing documentation (digest)"
Cohesion: 0.20
Nodes (9): Generics and variance, Protocols over ABCs, Python typing documentation (digest), strict-mode starter configuration, Syntax, by Python version, The core vocabulary, The pitfalls mypy catches that humans don't, What the checker is for (+1 more)

### Community 22 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 23 - "PEP 257 (digest)"
Cohesion: 0.22
Nodes (8): DRY: don't describe the interface twice, PEP 257 (digest), Semantics sections for exceptions and returns, Style notes the PEP settles, The multi-line rule, The one-line rule, What a docstring is, Where each docstring goes

### Community 24 - "PEP 8 (digest, with PEP 20)"
Cohesion: 0.22
Nodes (8): Comments, Comparisons, truth, and built-ins, Function and class conventions, Layout, Naming, PEP 8 (digest, with PEP 20), Programming recommendations, verbatim high-value list, The Zen of Python, applied

### Community 25 - "_load"
Cohesion: 0.36
Nodes (4): _load(), ManifestPairing, Path, skill_dirs()

### Community 26 - "Effective Python (digest)"
Cohesion: 0.25
Nodes (7): Classes and inheritance (Items 26-40+), Comprehensions and functions (Items 11-20+), Concurrency and parallelism (Items 67-80+), Effective Python (digest), Pythonic thinking (Items 1-10), Robustness and performance (Items 81-90+), The habits the book hammers

### Community 27 - "<app> API Designer"
Cohesion: 0.29
Nodes (6): <app> API Designer, Core Mission, Expertise Areas, Guiding Principles, Output Format, Quality Standards

### Community 28 - "<app> Migration Reviewer"
Cohesion: 0.29
Nodes (6): <app> Migration Reviewer, Core Mission, Expertise Areas, Guiding Principles, Output Format, Quality Standards

### Community 29 - "<app> Ownership Reviewer"
Cohesion: 0.29
Nodes (6): <app> Ownership Reviewer, Core Mission, Expertise Areas, Guiding Principles, Output Format, Quality Standards

### Community 30 - "<app> Architect Agent"
Cohesion: 0.29
Nodes (6): <app> Architect Agent, Core Mission, Expertise Areas, Guiding Principles, Output Format, Quality Standards

### Community 31 - "<app> Build Resolver Agent"
Cohesion: 0.29
Nodes (6): <app> Build Resolver Agent, Core Mission, Expertise Areas, Guiding Principles, Output Format, Quality Standards

### Community 32 - "<app> Code Explorer Agent"
Cohesion: 0.29
Nodes (6): <app> Code Explorer Agent, Core Mission, Expertise Areas, Guiding Principles, Output Format, Quality Standards

### Community 33 - "<app> Code Reviewer Agent"
Cohesion: 0.29
Nodes (6): <app> Code Reviewer Agent, Core Mission, Expertise Areas, Guiding Principles, Output Format, Quality Standards

### Community 34 - "<app> Planner Agent"
Cohesion: 0.29
Nodes (6): <app> Planner Agent, Core Mission, Expertise Areas, Guiding Principles, Output Format, Quality Standards

### Community 35 - "<app> TDD Guide Agent"
Cohesion: 0.29
Nodes (6): <app> TDD Guide Agent, Core Mission, Expertise Areas, Guiding Principles, Output Format, Quality Standards

### Community 36 - "<app> Depguard Reviewer"
Cohesion: 0.29
Nodes (6): <app> Depguard Reviewer, Core Mission, Expertise Areas, Guiding Principles, Output Format, Quality Standards

### Community 37 - "<app> Test Author"
Cohesion: 0.29
Nodes (6): <app> Test Author, Core Mission, Expertise Areas, Guiding Principles, Output Format, Quality Standards

### Community 38 - "<app> Add Handler"
Cohesion: 0.29
Nodes (6): <app> Add Handler, Core Principles, Output Format, Research References, Rules, When to Activate

### Community 39 - "<app> Add Module"
Cohesion: 0.29
Nodes (6): <app> Add Module, Core Principles, Output Format, Research References, Rules, When to Activate

### Community 40 - "<app> Claim Check skill"
Cohesion: 0.29
Nodes (6): <app> Claim Check skill, Core Principles, Output Format, Research References, Rules, When to Activate

### Community 41 - "<app> Clean-Room Rebuild skill"
Cohesion: 0.29
Nodes (6): <app> Clean-Room Rebuild skill, Core Principles, Output Format, Research References, Rules, When to Activate

### Community 42 - "<app> Corpus Retrieval skill"
Cohesion: 0.29
Nodes (6): <app> Corpus Retrieval skill, Core Principles, Output Format, Research References, Rules, When to Activate

### Community 43 - "<app> Depguard Guard"
Cohesion: 0.29
Nodes (6): <app> Depguard Guard, Core Principles, Output Format, Research References, Rules, When to Activate

### Community 44 - "<app> Diagnosing Bugs skill"
Cohesion: 0.29
Nodes (6): <app> Diagnosing Bugs skill, Core Principles, Output Format, Research References, Rules, When to Activate

### Community 45 - "<app> Domain Modeling skill"
Cohesion: 0.29
Nodes (6): <app> Domain Modeling skill, Core Principles, Output Format, Research References, Rules, When to Activate

### Community 46 - "<app> Grilling skill"
Cohesion: 0.29
Nodes (6): <app> Grilling skill, Core Principles, Output Format, Research References, Rules, When to Activate

### Community 47 - "<app> learn skill"
Cohesion: 0.29
Nodes (6): <app> learn skill, Core Principles, Output Format, Research References, Rules, When to Activate

### Community 48 - "<app> Ownership Author"
Cohesion: 0.29
Nodes (6): <app> Ownership Author, Core Principles, Output Format, Research References, Rules, When to Activate

### Community 49 - "<app> plan skill"
Cohesion: 0.29
Nodes (6): <app> plan skill, Core Principles, Output Format, Research References, Rules, When to Activate

### Community 50 - "<app> Research skill"
Cohesion: 0.29
Nodes (6): <app> Research skill, Core Principles, Output Format, Research References, Rules, When to Activate

### Community 51 - "<app> review skill"
Cohesion: 0.29
Nodes (6): <app> review skill, Core Principles, Output Format, Research References, Rules, When to Activate

### Community 52 - "<app> ship skill"
Cohesion: 0.29
Nodes (6): <app> ship skill, Core Principles, Output Format, Research References, Rules, When to Activate

### Community 53 - "<app> spec skill"
Cohesion: 0.29
Nodes (6): <app> spec skill, Core Principles, Output Format, Research References, Rules, When to Activate

### Community 54 - "<app> TDD skill"
Cohesion: 0.29
Nodes (6): <app> TDD skill, Core Principles, Output Format, Research References, Rules, When to Activate

### Community 55 - "<app> Verified Status skill"
Cohesion: 0.29
Nodes (6): <app> Verified Status skill, Core Principles, Output Format, Research References, Rules, When to Activate

### Community 56 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 57 - "build"
Cohesion: 0.53
Nodes (5): build(), main(), package_files(), Path, Files to package, relative to root, in a stable order.

### Community 58 - "beautifulpython — agent instructions"
Cohesion: 0.50
Nodes (3): beautifulpython — agent instructions, graphify, Model routing (Claude Code + Ollama)

### Community 59 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 60 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 61 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 62 - "guard-bash.sh"
Cohesion: 0.83
Nodes (3): has(), has_i(), guard-bash.sh script

## Knowledge Gaps
- **353 isolated node(s):** `$schema`, `name`, `version`, `description`, `name` (+348 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **37 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `write()` connect `CheckSkillTests` to `load_script`, `HarnessTest`?**
  _High betweenness centrality (0.010) - this node is a cross-community bridge._
- **Why does `load_script()` connect `load_script` to `test_ci_gates.py`, `CheckSkillTests`, `HarnessTest`?**
  _High betweenness centrality (0.007) - this node is a cross-community bridge._
- **What connects `Package marker for the deliberate-violations harness.`, `One deliberate violation per lint in lints/ruff.toml.  Each expect marker says w`, `The f-string belongs on its own variable, not inline in the raise.` to the rest of the system?**
  _385 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Path` be split into smaller, more focused modules?**
  _Cohesion score 0.10615079365079365 - nodes in this community are weakly interconnected._
- **Should `Beautiful Python` be split into smaller, more focused modules?**
  _Cohesion score 0.043478260869565216 - nodes in this community are weakly interconnected._
- **Should `load_script` be split into smaller, more focused modules?**
  _Cohesion score 0.06666666666666667 - nodes in this community are weakly interconnected._
- **Should `interface` be split into smaller, more focused modules?**
  _Cohesion score 0.06666666666666667 - nodes in this community are weakly interconnected._