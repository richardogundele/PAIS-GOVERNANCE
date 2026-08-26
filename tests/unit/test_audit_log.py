import json

from pais_governance.core.audit_log import AuditEvent, AuditLogger


def test_hash_chain_is_valid_and_detects_tampering(tmp_path):
    path = tmp_path / "audit.jsonl"
    logger = AuditLogger(str(path))
    logger.append(AuditEvent(event_type="ALLOW", actor="agent-1"))
    logger.append(AuditEvent(event_type="BLOCK_ACTION", actor="agent-2"))

    assert logger.verify_integrity()["valid"] is True

    records = [json.loads(line) for line in path.read_text().splitlines()]
    records[0]["actor"] = "tampered"
    path.write_text("\n".join(json.dumps(record) for record in records) + "\n")
    reloaded = AuditLogger(str(path))
    result = reloaded.verify_integrity()
    assert result["valid"] is False
    assert result["events_checked"] == 0


def test_request_is_fingerprinted_not_copied_into_event(tmp_path):
    logger = AuditLogger(str(tmp_path / "audit.jsonl"))
    request = {"agent_id": "agent-1", "data": {"national_id": "secret-value"}}
    fingerprint = logger.fingerprint(request)
    assert len(fingerprint) == 64
    assert "secret-value" not in fingerprint
