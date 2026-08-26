# Changelog

This project follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and semantic versioning from the first tagged alpha release.

## Unreleased

### Changed

- repositioned PAIS as an agent reliability and policy gateway
- replaced unsupported integration and compliance claims with an explicit capability boundary
- replaced permissive unknown-action behaviour with configurable fail-safe review
- added deny-overrides precedence and auditable condition operators
- added hash-linked audit events and integrity verification
- added a strict FastAPI decision contract and pending-review status
- moved spreadsheet redaction dependencies into an optional extra
- added Python 3.10/3.12 CI, coverage enforcement and a container build

### Security

- audit events fingerprint request bodies instead of copying payload content
- CORS methods and headers are restricted in the default API configuration

## Historical repository state — 2026-05-11

The initial repository contained a policy engine, spreadsheet redaction code, an API prototype and documentation. It was not published as a tagged release. Several historical documentation claims were not supported by implemented adapters or public evidence and were removed before v0.1.0.
