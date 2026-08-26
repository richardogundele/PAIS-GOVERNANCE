"""Deterministic policy evaluation for agent and data operations."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

import yaml


class PolicyAction(str, Enum):
    ALLOW = "ALLOW"
    LOG_FOR_AUDIT = "LOG_FOR_AUDIT"
    WARN_AND_REDACT = "WARN_AND_REDACT"
    REQUIRE_HUMAN_REVIEW = "REQUIRE_HUMAN_REVIEW"
    BLOCK_ACTION = "BLOCK_ACTION"


ACTION_PRECEDENCE = {
    PolicyAction.ALLOW: 0,
    PolicyAction.LOG_FOR_AUDIT: 1,
    PolicyAction.WARN_AND_REDACT: 2,
    PolicyAction.REQUIRE_HUMAN_REVIEW: 3,
    PolicyAction.BLOCK_ACTION: 4,
}


def _matches_value(actual: Any, expected: Any) -> bool:
    """Evaluate the intentionally small condition language."""
    if isinstance(expected, list):
        return actual in expected
    if not isinstance(expected, Mapping):
        return actual == expected
    for operator, value in expected.items():
        if operator == "in" and actual not in value:
            return False
        if operator == "not_in" and actual in value:
            return False
        if operator == "gte" and (actual is None or actual < value):
            return False
        if operator == "lte" and (actual is None or actual > value):
            return False
        if operator == "contains" and (actual is None or value not in actual):
            return False
        if operator == "exists" and (actual is not None) is not bool(value):
            return False
    return True


@dataclass(frozen=True)
class PolicyRule:
    """A named rule evaluated against a normalised request."""

    name: str
    trigger: str
    action: PolicyAction
    condition: dict[str, Any] = field(default_factory=dict)
    reason: str = ""
    sensitive_fields: list[str] = field(default_factory=list)
    approval_required_from: list[str] = field(default_factory=list)
    escalation_timeout_hours: int = 24
    priority: int = 100
    enabled: bool = True

    @property
    def sensitive_columns(self) -> list[str]:
        return self.sensitive_fields

    def matches(self, request: Mapping[str, Any]) -> bool:
        if not self.enabled or request.get("trigger") != self.trigger:
            return False
        return all(_matches_value(request.get(key), value) for key, value in self.condition.items())


@dataclass(frozen=True)
class PolicyDecision:
    action: PolicyAction
    rule_name: str
    reason: str
    sensitive_fields: list[str] = field(default_factory=list)
    approval_required_from: list[str] = field(default_factory=list)
    escalation_timeout_hours: int = 24
    decision_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def sensitive_columns(self) -> list[str]:
        return self.sensitive_fields


class PolicyEngine:
    """Evaluate all matching rules and choose the safest highest-priority result."""

    def __init__(
        self,
        rules: Iterable[PolicyRule] | None = None,
        default_action: PolicyAction = PolicyAction.REQUIRE_HUMAN_REVIEW,
    ) -> None:
        self.rules = list(rules or [])
        self.default_action = default_action

    @classmethod
    def from_config(cls, config: Mapping[str, Any]) -> PolicyEngine:
        policy_config = config.get("policy", {})
        default_action = PolicyAction(policy_config.get("default_action", "REQUIRE_HUMAN_REVIEW"))
        rules = []
        for item in config.get("policies", config.get("rules", [])) or []:
            rules.append(
                PolicyRule(
                    name=item["name"],
                    trigger=item["trigger"],
                    action=PolicyAction(str(item["action"]).upper()),
                    condition=dict(item.get("condition") or {}),
                    reason=item.get("reason", ""),
                    sensitive_fields=list(
                        item.get("sensitive_fields", item.get("sensitive_columns", []))
                    ),
                    approval_required_from=list(item.get("approval_required_from", [])),
                    escalation_timeout_hours=int(item.get("escalation_timeout_hours", 24)),
                    priority=int(item.get("priority", 100)),
                    enabled=bool(item.get("enabled", True)),
                )
            )
        return cls(rules, default_action)

    @classmethod
    def load_config(cls, config_path: str) -> PolicyEngine:
        with open(config_path, encoding="utf-8") as handle:
            return cls.from_config(yaml.safe_load(handle) or {})

    def add_rule(self, rule: PolicyRule) -> None:
        self.rules.append(rule)

    def evaluate(self, request: Mapping[str, Any]) -> PolicyDecision:
        matches = [rule for rule in self.rules if rule.matches(request)]
        if not matches:
            return PolicyDecision(
                action=self.default_action,
                rule_name="default",
                reason=f"No rule matched; default action is {self.default_action.value}",
            )
        selected = max(matches, key=lambda rule: (ACTION_PRECEDENCE[rule.action], rule.priority))
        return PolicyDecision(
            action=selected.action,
            rule_name=selected.name,
            reason=selected.reason or f"Matched policy rule: {selected.name}",
            sensitive_fields=selected.sensitive_fields,
            approval_required_from=selected.approval_required_from,
            escalation_timeout_hours=selected.escalation_timeout_hours,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "default_action": self.default_action.value,
            "rules": [
                {
                    "name": r.name,
                    "trigger": r.trigger,
                    "action": r.action.value,
                    "condition": r.condition,
                    "reason": r.reason,
                    "priority": r.priority,
                    "enabled": r.enabled,
                }
                for r in self.rules
            ],
        }


class PolicyBuilder:
    def __init__(self) -> None:
        self.rules: list[PolicyRule] = []

    def add_rule(self, name: str, trigger: str, action: str, **kwargs: Any) -> PolicyBuilder:
        self.rules.append(
            PolicyRule(name=name, trigger=trigger, action=PolicyAction(action.upper()), **kwargs)
        )
        return self

    def build(self) -> PolicyEngine:
        return PolicyEngine(self.rules)


def create_default_policies() -> list[PolicyRule]:
    return [
        PolicyRule(
            name="allow_read_only_tools",
            trigger="agent_tool_call",
            action=PolicyAction.ALLOW,
            condition={
                "operation": "read",
                "environment": {"in": ["development", "staging"]},
            },
            reason="Read-only operation in a non-production environment",
        ),
        PolicyRule(
            name="review_production_side_effects",
            trigger="agent_tool_call",
            action=PolicyAction.REQUIRE_HUMAN_REVIEW,
            condition={"environment": "production", "has_side_effect": True},
            reason="Production side effects require explicit human approval",
            approval_required_from=["service-owner"],
            priority=500,
        ),
        PolicyRule(
            name="block_destructive_shell",
            trigger="agent_tool_call",
            action=PolicyAction.BLOCK_ACTION,
            condition={"tool": "shell", "operation": {"in": ["delete", "reset", "destroy"]}},
            reason="Destructive shell operations are denied by policy",
            priority=1000,
        ),
    ]
