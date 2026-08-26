import yaml
from fastapi.testclient import TestClient

from pais_governance.server import app


def test_api_decision_health_audit_and_review(monkeypatch, tmp_path):
    config_path = tmp_path / "pais.yaml"
    config_path.write_text(
        yaml.safe_dump(
            {
                "policy": {"default_action": "REQUIRE_HUMAN_REVIEW"},
                "policies": [
                    {
                        "name": "block-delete",
                        "trigger": "agent_tool_call",
                        "action": "BLOCK_ACTION",
                        "condition": {"tool": "shell", "operation": "delete"},
                    }
                ],
                "audit": {"log_file": str(tmp_path / "audit.jsonl")},
            }
        )
    )
    monkeypatch.setenv("PAIS_CONFIG", str(config_path))

    with TestClient(app) as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["audit_integrity"] is True

        blocked = client.post(
            "/api/v1/decisions",
            json={
                "agent_id": "agent-1",
                "tool": "shell",
                "operation": "delete",
                "environment": "production",
            },
        )
        assert blocked.status_code == 200
        assert blocked.json()["action"] == "BLOCK_ACTION"

        review = client.post(
            "/api/v1/decisions",
            json={"agent_id": "agent-2", "tool": "payments", "operation": "write"},
        ).json()
        status = client.get(f"/api/v1/reviews/{review['decision_id']}")
        assert status.status_code == 200
        assert status.json()["status"] == "PENDING"

        events = client.get("/api/v1/audit/events?limit=10")
        assert events.json()["count"] == 2
        assert client.get("/api/v1/audit/integrity").json()["valid"] is True

        assert client.get("/api/v1/reviews/not-found").status_code == 404
        assert client.get("/api/v1/audit/events?limit=0").status_code == 422
        assert (
            client.post(
                "/api/v1/decisions",
                json={"agent_id": "", "tool": "shell", "operation": "read"},
            ).status_code
            == 422
        )
