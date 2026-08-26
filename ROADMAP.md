# PAIS roadmap

PAIS is an alpha project. Roadmap items are proposals until code, tests and release notes demonstrate otherwise.

## v0.1 — reliable decision boundary

- [x] deterministic YAML policy engine
- [x] deny-overrides rule precedence
- [x] fail-safe default outcome
- [x] mapping-field redaction
- [x] pending-review metadata
- [x] hash-linked audit records and integrity verification
- [x] FastAPI boundary, tests, CI and container build

## v0.2 — durable operations

- [ ] PostgreSQL-backed decisions and approval queue
- [ ] idempotency keys and replay protection
- [ ] signed audit checkpoints
- [ ] policy validation command and dry-run mode
- [ ] OpenTelemetry decision traces

## v0.3 — framework adapters

- [ ] OpenAI Agents SDK tool wrapper
- [ ] Model Context Protocol proxy adapter
- [ ] LangGraph middleware
- [ ] Azure identity example deployment

## Evidence milestones

- [ ] publish independently reproducible latency and throughput results
- [ ] document three external design-partner evaluations
- [ ] complete the first external contributor pull request
- [ ] publish a threat model and independent security review

Project direction will be driven by reproducible evidence and user reports rather than unverified adoption claims.
