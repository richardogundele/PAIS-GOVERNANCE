# PAIS Agent Reliability Gateway

[![CI](https://github.com/richardogundele/PAIS-GOVERNANCE/actions/workflows/ci.yml/badge.svg)](https://github.com/richardogundele/PAIS-GOVERNANCE/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status: Alpha](https://img.shields.io/badge/status-alpha-orange.svg)](ROADMAP.md)

**An open-source policy boundary for AI-agent tool calls.**

PAIS evaluates a proposed agent action *before* it reaches a tool. It returns one of five explicit outcomes: `ALLOW`, `LOG_FOR_AUDIT`, `WARN_AND_REDACT`, `REQUIRE_HUMAN_REVIEW` or `BLOCK_ACTION`. Every decision is appended to a hash-linked audit trail so later modification can be detected.

PAIS does not execute tools and does not pretend to make an agent safe by itself. The host application must call PAIS before execution and honour its decision.

## Why this exists

Agent frameworks make it easy to give models access to databases, shells, communication systems and production APIs. The difficult operational questions remain:

- Which tools may this agent call in this environment?
- Which actions require a human before they create an external side effect?
- What happens when a new action has no matching policy?
- Can an investigator verify which policy produced a decision?
- Can confidential fields be removed without logging their values?

PAIS provides a small, inspectable reliability boundary for those questions.

## Implemented in v0.1

- YAML policy-as-code with exact, membership, range, containment and existence conditions
- Deny-overrides precedence when multiple rules match
- Fail-safe default for unknown actions
- Human-review queue metadata for escalated decisions
- Field-level redaction for mapping payloads
- Append-only JSONL audit events linked by SHA-256 hashes
- Audit-chain integrity verification
- FastAPI decision, audit and review-status endpoints
- Docker build and Python 3.10/3.12 CI

## Not implemented yet

The following are roadmap items, not current claims:

- execution adapters for Azure OpenAI, OpenAI Agents SDK, MCP or LangGraph
- durable multi-node approval storage
- authentication and enterprise identity integration
- signed audit checkpoints or external transparency logs
- policy simulation UI and production performance evidence

See [ROADMAP.md](ROADMAP.md) and [the architecture notes](docs/ARCHITECTURE.md).

## Quick start

```bash
git clone https://github.com/richardogundele/PAIS-GOVERNANCE.git
cd PAIS-GOVERNANCE
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn pais_governance.server:app --reload
```

Request a decision:

```bash
curl -s http://127.0.0.1:8000/api/v1/decisions \
  -H 'content-type: application/json' \
  -d '{
    "agent_id": "operations-agent",
    "tool": "shell",
    "operation": "delete",
    "environment": "production",
    "has_side_effect": true,
    "risk_score": 90
  }'
```

Response:

```json
{
  "action": "BLOCK_ACTION",
  "rule": "block-destructive-shell",
  "reason": "Destructive shell operations are denied by policy"
}
```

Decision IDs and timestamps are omitted from this abbreviated example.

## Use as a Python library

```python
from pais_governance import PolicyGateway

gateway = PolicyGateway.from_config_file("pais_config.yaml")
decision = gateway.enforce_policy({
    "agent_id": "support-agent",
    "tool": "customer-records",
    "operation": "read",
    "environment": "staging",
    "data_classification": "internal",
})

if decision["action"] == "ALLOW":
    # The host application, not PAIS, may now invoke the tool.
    pass
```

## Policy example

```yaml
policy:
  default_action: "REQUIRE_HUMAN_REVIEW"

policies:
  - name: "review-production-side-effects"
    trigger: "agent_tool_call"
    action: "REQUIRE_HUMAN_REVIEW"
    reason: "Production side effects require explicit human approval"
    approval_required_from: ["service-owner"]
    condition:
      environment: "production"
      has_side_effect: true

  - name: "block-destructive-shell"
    trigger: "agent_tool_call"
    action: "BLOCK_ACTION"
    priority: 1000
    reason: "Destructive shell operations are denied by policy"
    condition:
      tool: "shell"
      operation:
        in: ["delete", "reset", "destroy"]
```

When multiple rules match, PAIS chooses the safest outcome. Within the same outcome, the higher numeric priority wins.

## Run the checks

```bash
pip install -e '.[dev]'
ruff check src tests
pytest --cov=pais_governance --cov-report=term-missing
docker build -t pais-agent-gateway:local .
```

The repository includes a reproducible local benchmark harness in [`scripts/benchmark.py`](scripts/benchmark.py). No performance claim is published until results are independently reproducible.

## Security model

PAIS is a decision point, not an execution sandbox. It reduces ambiguity at the tool boundary but cannot prevent a host application from ignoring a decision. The JSONL chain is tamper-evident, not tamper-proof: production deployments should checkpoint the head hash to independently controlled storage.

Please read [SECURITY.md](SECURITY.md) before deployment or reporting a vulnerability.

## Contributing

PAIS is in alpha and welcomes focused contributions in policy evaluation, approval durability, signed audit checkpoints and framework adapters. Start with [CONTRIBUTING.md](CONTRIBUTING.md) and an issue describing the behaviour you want to change.

## Maintainer

PAIS was created and is maintained by [Richard Ogundele](https://github.com/richardogundele), an Enterprise AI Solution Architect working on scalable AI platforms, agentic systems and production reliability.

## Licence

[MIT](LICENSE)
