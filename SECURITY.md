# Security policy

PAIS is alpha software and has not received an independent security audit. Do not treat it as a complete security boundary for production agents.

## Report a vulnerability

Use GitHub's **Report a vulnerability** private security-advisory flow for this repository. Do not open a public issue containing exploit details, credentials or personal data.

Include the affected commit or version, reproduction steps, impact and any suggested mitigation. No guaranteed response or remediation timeline is claimed at this stage, but reports will be triaged as quickly as maintainer capacity allows.

## Current trust assumptions

- the host application calls PAIS before every protected tool invocation
- the host application honours `BLOCK_ACTION` and `REQUIRE_HUMAN_REVIEW`
- the policy file and PAIS service are protected from unauthorised modification
- audit storage permissions are independently controlled
- authentication, rate limiting and transport security are supplied by the deployment environment

## Important limitations

- the API does not yet include built-in authentication
- the local review queue is not durable across restarts
- the hash-linked audit file is tamper-evident, not tamper-proof
- PAIS does not sandbox or execute tools
- field redaction is configuration-based and is not a general-purpose PII detector

Production evaluation should include threat modelling, authentication, a durable database, signed audit checkpoints, restrictive network policy and an independent review.
