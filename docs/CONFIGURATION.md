# Configuration reference

PAIS reads `pais_config.yaml`, or the file named by `PAIS_CONFIG`.

## Default action

```yaml
policy:
  default_action: "REQUIRE_HUMAN_REVIEW"
```

Supported actions are `ALLOW`, `LOG_FOR_AUDIT`, `WARN_AND_REDACT`, `REQUIRE_HUMAN_REVIEW` and `BLOCK_ACTION`.

## Conditions

A scalar condition requires equality. A list means the request value must be one of the listed values. Operator mappings support `in`, `not_in`, `gte`, `lte`, `contains` and `exists`.

```yaml
condition:
  environment: "production"
  risk_score:
    gte: 70
  operation:
    in: ["write", "send"]
```

All conditions within a rule must match. When several rules match, the strongest action wins. A numeric `priority` breaks ties between rules with the same action.

## Audit path

```yaml
audit:
  log_file: "logs/audit.jsonl"
```

Use storage permissions appropriate for sensitive operational metadata. For production evaluation, independently checkpoint or sign the audit head hash.
