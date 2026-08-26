"""Policy gateway for AI-agent tool calls and sensitive-data operations."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

from pais_governance.core.audit_log import AuditLogger
from pais_governance.core.policy_engine import PolicyAction, PolicyEngine


class PolicyGateway:
    """Return a decision before a caller executes an agent action.

    PAIS does not execute tools. The host application must honour the decision.
    This boundary keeps the policy layer deterministic and integration-agnostic.
    """

    def __init__(self, config: dict[str, Any], audit_logger: AuditLogger | None = None) -> None:
        self.config = config
        self.policy_engine = PolicyEngine.from_config(config)
        audit_path = config.get("audit", {}).get("log_file", "logs/audit.jsonl")
        self.audit_logger = audit_logger or AuditLogger(audit_path)
        self.pending_reviews: dict[str, dict[str, Any]] = {}

    @classmethod
    def from_config_file(cls, config_path: str) -> PolicyGateway:
        with open(config_path, encoding="utf-8") as handle:
            return cls(yaml.safe_load(handle) or {})

    def enforce_policy(self, request: dict[str, Any]) -> dict[str, Any]:
        normalised = self._normalise(request)
        decision = self.policy_engine.evaluate(normalised)
        safe_data = normalised.get("data")
        if decision.action == PolicyAction.WARN_AND_REDACT:
            safe_data = self._redact_mapping(safe_data, decision.sensitive_fields)

        self.audit_logger.log_decision(normalised, decision)
        response: dict[str, Any] = {
            "decision_id": decision.decision_id,
            "action": decision.action.value,
            "rule": decision.rule_name,
            "decision": decision.rule_name,
            "reason": decision.reason,
            "timestamp": decision.timestamp,
        }
        if decision.action == PolicyAction.WARN_AND_REDACT:
            response["safe_data"] = safe_data
            response["redacted_fields"] = decision.sensitive_fields
        if decision.action == PolicyAction.REQUIRE_HUMAN_REVIEW:
            self.pending_reviews[decision.decision_id] = {
                "request_fingerprint": AuditLogger.fingerprint(normalised),
                "status": "PENDING",
                "required_from": decision.approval_required_from,
                "timeout_hours": decision.escalation_timeout_hours,
            }
            response["review"] = self.pending_reviews[decision.decision_id]
        return response

    def _normalise(self, request: dict[str, Any]) -> dict[str, Any]:
        result = deepcopy(request)
        result.setdefault("trigger", "agent_tool_call")
        result.setdefault("environment", "development")
        read_only_operations = {"read", "list", "search", "inspect"}
        result.setdefault("has_side_effect", result.get("operation") not in read_only_operations)
        return result

    @staticmethod
    def _redact_mapping(data: Any, fields: list[str]) -> Any:
        if not isinstance(data, dict):
            return data
        output = deepcopy(data)
        for field in fields:
            if field in output:
                output[field] = "[REDACTED]"
        return output

    def handle_file_share(
        self, file_path: str, shared_by: str, shared_with: str, is_external: bool = True
    ) -> dict[str, Any]:
        return self.enforce_policy(
            {
                "trigger": "file_shared_externally" if is_external else "file_shared_internally",
                "file": file_path,
                "shared_by": shared_by,
                "shared_with": shared_with,
                "is_external": is_external,
            }
        )

    def handle_ai_upload(
        self, file_path: str, user: str, destination: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        return self.enforce_policy(
            {
                "trigger": "data_uploaded_to_ai",
                "file": file_path,
                "user": user,
                "destination": destination,
                "data": data,
            }
        )


def load_gateway(config_path: str | Path = "pais_config.yaml") -> PolicyGateway:
    return PolicyGateway.from_config_file(str(config_path))
