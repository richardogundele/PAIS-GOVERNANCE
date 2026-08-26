# Architecture

## Trust boundary

```text
Agent runtime
    |
    | proposed tool call
    v
PAIS decision API ----> policy engine ----> explicit outcome
    |                         |
    |                         +-----------> hash-linked audit event
    v
Host application honours outcome
    |
    +-- ALLOW / redacted payload ---> tool
    +-- REVIEW ---------------------> human workflow
    +-- BLOCK ----------------------> no execution
```

PAIS deliberately does not own tool execution. This keeps policy decisions deterministic and makes the integration contract testable. The host remains responsible for preventing bypass.

## Decision semantics

Rules match a trigger and optional conditions. When several rules match, the outcome with the strongest safety precedence wins:

`BLOCK_ACTION > REQUIRE_HUMAN_REVIEW > WARN_AND_REDACT > LOG_FOR_AUDIT > ALLOW`

An unknown action uses the configured default, which is `REQUIRE_HUMAN_REVIEW` in the example policy.

## Audit integrity

Each JSONL event contains the previous event hash. The current event hash covers every field except itself. `verify_integrity()` recalculates the chain from the genesis value and reports the first invalid event.

This detects local modification. It does not stop an administrator from replacing the entire log and is therefore not described as immutable. A production design should periodically sign and checkpoint the head hash outside the PAIS trust boundary.

## Data handling

The audit event stores a SHA-256 fingerprint of the normalised request rather than the request body. This reduces accidental replication of sensitive payloads. Operators must still treat fingerprints and metadata as potentially sensitive operational records.
