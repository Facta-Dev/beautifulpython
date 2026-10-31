# FastAPI, TaskIQ, and the backend stack (framework digest)

Source: this digest is written for the FastAPI + TaskIQ + Dragonfly (Redis
protocol) + Postgres/pgvector backend stack, following a vertical-slicing,
hexagonal-architecture layout (see the facta backend-python guides:
hexagonal architecture, vertical slicing, dependency rules). It is the Python
analogue of what a Bevy digest does for game code: name the conventions to leave
alone, and the bugs that pass every lint.

## What changes from the general rules

These rules from `SKILL.md` **do not apply** to framework-managed code:

- **"Validate everything yourself at the boundary"** — FastAPI already validates:
  parameters annotated `Path`/`Query`/`Body`/`Header` are parsed and rejected before
  the handler runs. Don't re-validate with `try: int(x)` inside a handler; annotate
  the parameter and let the framework produce the 422.
- **"Pydantic models keep their fields private"** — wrong for the stack: pydantic
  models ARE the public data contract (request/response models). Public typed fields,
  `model_config = ConfigDict(...)`, and validators are the point. Keep private
  attributes for domain logic only, and never put behavior you can't serialize on a
  model that crosses the wire.
- **"Hand-roll DI with small factories"** — the framework owns the graph. Use
  `Depends` for request-scoped dependencies and TaskIQ's broker DI for task ones; a
  hand-built object graph that bypasses `Depends` produces duplicates that don't
  share the request's lifespan and won't close.
- **"Avoid module-level mutable state"** — connection pools, brokers, and engine/pool
  objects are legitimately module- or app-scoped singletons; they are explicitly
  initialized once in the composition root (app startup / lifespan), not per request.
  What stays forbidden: mutable business state at module level.
- **"Use dataclasses for records"** — pydantic `BaseModel` at boundaries; SQLAlchemy
  ORM models in adapters; plain frozen dataclasses still own the domain ring.

## Layout: hexagonal + vertical slicing

- **Rings:** `composition` (root, knows everything) → slices → `ports` (Protocols) →
  `domain` (pure, zero-I/O). Dependencies point inward only; `domain` imports nothing
  from the stack — no `fastapi`, no `sqlalchemy`, no `httpx`.
- **Slices don't import each other.** A new feature is a new slice; shared behavior
  moves down into `ports`/`domain`, not sideways.
- **Ports are Protocols; use-cases depend on the Protocol, not the adapter.** The
  composition root picks `PgWidgetRepository` vs. the fake. `mypy --strict` verifies
  the injected instance satisfies the Protocol.
- **Imports enforced, not remembered:** `import-linter` (layered + forbidden +
  independence contracts), ruff banned imports (`TID251`/`TID252`), mypy strict.
  Python has no compile-time graph; the contracts are the graph.

## Quiet failure modes that every lint passes

These are the bugs the machine checks cannot see:

1. **Async handlers calling sync, CPU- or I/O-blocking work** — a sync `requests.get`
   or `time.sleep` inside a `def` (fine) vs `async def` handler (blocks the event
   loop for every request). Any blocking call inside `async def` must go through
   `run_in_executor`/`anyio.to_thread` or move to the task queue.
2. **Background tasks vs TaskIQ** — `BackgroundTasks` runs in-process after the
   response; a crash or restart loses it. Anything that must survive dispatches
   through the TaskIQ broker. Don't hand both without deciding which guarantee the
   caller gets.
3. **Task handlers depending on request-scoped things** — a TaskIQ worker process has
   no `Depends` from the web process. Handlers receive their own broker DI; a session
   or client must be constructed in the worker, not captured from a request
   closure.
4. **Lifespan-managed clients leaking into tasks** — a `httpx.AsyncClient` created in
   FastAPI's lifespan and captured by a task closure is closed (or worse, alive in a
   different process) when the worker runs it. Workers own their clients.
5. **Dragonfly/Redis keys without an owner or TTL** — every key names its service
   (`cache:user:{id}`), and transient keys carry an expiry. A key written with an
   unbounded TTL is a production incident in a year.
6. **Transactions spanning awaits on unrelated I/O** — a SQLAlchemy session with an
   open transaction while awaiting an HTTP call holds a pooled connection for the
   whole round trip. Commit or roll back before awaiting anything that isn't the
   database; the pool exhaustion shows up as latency, not as an error.
7. **pgvector: distance functions on untyped columns** — a `vector` column indexed
   with one metric (cosine) queried with another (L2) returns plausible but wrong
   neighbors. Pin the metric at the adapter, test with a hand-checked example, and
   keep SQL inside the adapter layer.
8. **Pydantic v2 vs v1 drift** — `.dict()`/`parse_obj` are v1; `model_dump()`/
   `model_validate()` are v2. Mixed conventions in one repo mean half the validators
   quietly never run. Pin one major version in `pyproject.toml`.
9. **`Depends` caching surprises** — dependencies are cached per-request by default;
   `use_cache=False` when a dependency's identity matters. A "fresh client each call"
   expectation without that flag is a shared-client bug in disguise.
10. **Serialization of domain exceptions** — the port maps
    `sqlalchemy.SQLAlchemyError`/broker errors into domain errors; the router maps
    domain errors into HTTP statuses in one place (an exception handler), not in
    every slice. A traceback escaping to a client is a leak, and so is a 500 that
    should have been a 409.

## Lint allowances this stack needs

When a repo uses the stack, its ruff config needs on top of `lints/ruff.toml`:

- `B008` allow for `Depends(...)`/`Query(...)`/`Path(...)`/`Body(...)` in parameter
  defaults — that IS the framework's API (per-file or per-project ignore).
- `RUF012` allow for mutable `ClassVar` defaults on pydantic models' `model_config`.
- `UP007`/`UP045` may need care if the framework or its plugins still expect the
  `Optional` spelling on older Python baselines.
- `TID251`/`TID252` banned imports: forbid `fastapi`/`sqlalchemy`/`httpx` inside the
  domain package, and `sqlalchemy` outside `ports/` — the import-linter contracts
  need the lint-grade backup at file granularity.
- `S101` stays forbidden, but note `assert` inside pytest files is allowed via
  `per-file-ignores`.

## Verification the stack needs beyond the checker

- import-linter contracts run in CI (`lint-imports`).
- Domain purity: a test imports `<app>.domain` and asserts no stack module appears —
  cheap regression for the architecture's core rule.
- Each slice installable independently (independence contract) keeps slicing honest.
