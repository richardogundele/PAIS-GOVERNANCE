from pais_governance.core.policy_engine import PolicyAction, PolicyEngine

CONFIG = {
    "policy": {"default_action": "REQUIRE_HUMAN_REVIEW"},
    "policies": [
        {
            "name": "allow-read",
            "trigger": "agent_tool_call",
            "action": "ALLOW",
            "condition": {"operation": {"in": ["read", "list"]}},
        },
        {
            "name": "review-risk",
            "trigger": "agent_tool_call",
            "action": "REQUIRE_HUMAN_REVIEW",
            "priority": 500,
            "condition": {"risk_score": {"gte": 70}},
        },
        {
            "name": "block-delete",
            "trigger": "agent_tool_call",
            "action": "BLOCK_ACTION",
            "priority": 1000,
            "condition": {"tool": "shell", "operation": "delete"},
        },
    ],
}


def test_allows_matching_read_operation():
    decision = PolicyEngine.from_config(CONFIG).evaluate(
        {"trigger": "agent_tool_call", "tool": "database", "operation": "read", "risk_score": 5}
    )
    assert decision.action == PolicyAction.ALLOW
    assert decision.rule_name == "allow-read"


def test_deny_rule_wins_when_multiple_rules_match():
    decision = PolicyEngine.from_config(CONFIG).evaluate(
        {"trigger": "agent_tool_call", "tool": "shell", "operation": "delete", "risk_score": 90}
    )
    assert decision.action == PolicyAction.BLOCK_ACTION
    assert decision.rule_name == "block-delete"


def test_unknown_action_fails_safe_to_review():
    decision = PolicyEngine.from_config(CONFIG).evaluate(
        {"trigger": "agent_tool_call", "tool": "new-tool", "operation": "write", "risk_score": 10}
    )
    assert decision.action == PolicyAction.REQUIRE_HUMAN_REVIEW
    assert decision.rule_name == "default"
