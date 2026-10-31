# Architecture diagrams

Interactive Archify diagrams for the stack this repo teaches: FastAPI +
TaskIQ + Dragonfly (Redis protocol) + Postgres/pgvector + SQLAlchemy 2.0 async,
laid out hexagonal with vertical slices and enforced by import-linter.
Each diagram is a standalone HTML page (open it in any browser); the JSON next
to it is the source.

| Diagram | Type | What it shows | Source | Rendered |
|---|---|---|---|---|
| c4-containers | architecture | Containers: browser/SDK clients, FastAPI API, Dragonfly broker, PostgreSQL + pgvector, TaskIQ worker, OIDC IdP, outside vendors | [json](c4-containers.json) | [html](c4-containers.html) |
| services-slices | architecture | The uv-workspace package map: composition → slices → ports (Protocols · Pg* adapters) → domain, with broker and task workers | [json](services-slices.architecture.json) | [html](services-slices.architecture.html) |
| auth-algorithm | workflow | The auth pipeline as an algorithm: signup → verification code → login gates (authenticate · rate-limit · authorize) → token mint and audit | [json](auth-algorithm.workflow.json) | [html](auth-algorithm.workflow.html) |
| outbox-algorithm | workflow | Durable task delivery: transactional commit, `.kiq` dispatch through the Dragonfly broker, worker consume, backoff and dead-letter | [json](outbox-algorithm.workflow.json) | [html](outbox-algorithm.workflow.html) |
| auth-sequence | sequence | Signup-to-login trace: one transaction for the state write, TaskIQ dispatch, code delivery, verify, then token mint with rotating refresh | [json](auth-sequence.sequence.json) | [html](auth-sequence.sequence.html) |
| outbox-sequence | sequence | Producer/broker/worker trace for one queued email: commit, fetch, send, ack, retry policy and the janitor sweep | [json](outbox-sequence.sequence.json) | [html](outbox-sequence.sequence.html) |
| database-dataflow | dataflow | Data flow across clients → use-cases → Postgres/pgvector storage → Dragonfly queue → email delivery, with tx enqueue and retry edges | [json](database-dataflow.dataflow.json) | [html](database-dataflow.dataflow.html) |
| runtime-lifecycle | lifecycle | Runtime states from boot: pydantic-settings validate-on-boot, lifespan wiring, readyz gate, request flow, worker drain, degraded and fatal endings | [json](runtime-lifecycle.lifecycle.json) | [html](runtime-lifecycle.lifecycle.html) |

Authored with Archify; sibling set of the facta backend template.