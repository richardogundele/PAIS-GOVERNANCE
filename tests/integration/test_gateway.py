from pais_governance.core.audit_log import AuditLogger
from pais_governance.core.gateway import PolicyGateway


def gateway(tmp_path):
    config = {
        "policy": {"default_action": "REQUIRE_HUMAN_REVIEW"},
        "policies": [
            {
                "name": "redact-contact",
                "trigger": "agent_tool_call",
                "action": "WARN_AND_REDACT",
                "sensitive_fields": ["email"],
                "condition": {"data_classification": "confidential"},
            },
            {
                "name": "allow-read",
                "trigger": "agent_tool_call",
                "action": "ALLOW",
                "condition": {"operation": "read"},
            },
        ],
    }
    return PolicyGateway(config, AuditLogger(str(tmp_path / "audit.jsonl")))


def test_redacts_configured_field_and_records_decision(tmp_path):
    service = gateway(tmp_path)
    result = service.enforce_policy(
        {
            "agent_id": "research-agent",
            "tool": "crm",
            "operation": "send",
            "data_classification": "confidential",
            "data": {"email": "person@example.com", "case_id": "C-17"},
        }
    )
    assert result["action"] == "WARN_AND_REDACT"
    assert result["safe_data"] == {"email": "[REDACTED]", "case_id": "C-17"}
    assert service.audit_logger.verify_integrity()["events_checked"] == 1


def test_unmatched_write_creates_pending_review(tmp_path):
    service = gateway(tmp_path)
    result = service.enforce_policy(
        {"agent_id": "agent-1", "tool": "payments", "operation": "write"}
    )
    assert result["action"] == "REQUIRE_HUMAN_REVIEW"
    assert result["review"]["status"] == "PENDING"
    assert result["decision_id"] in service.pending_reviews
