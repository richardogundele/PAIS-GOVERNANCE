"""Append-only, tamper-evident audit records for PAIS decisions."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

GENESIS_HASH = "0" * 64


def _canonical(data: dict[str, Any]) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


@dataclass
class AuditEvent:
    event_type: str
    actor: str | None = None
    action: str | None = None
    resource: str | None = None
    decision: str | None = None
    reason: str | None = None
    request_fingerprint: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    previous_hash: str = GENESIS_HASH
    event_hash: str = ""

    def payload(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop("event_hash", None)
        return data

    def seal(self) -> None:
        self.event_hash = hashlib.sha256(_canonical(self.payload())).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class AuditLogger:
    """Persist JSONL events linked by hashes so tampering can be detected."""

    def __init__(self, log_file: str | None = None) -> None:
        self.log_file = Path(log_file or "audit.log")
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.log_file.touch(exist_ok=True)
        self.events: list[AuditEvent] = []
        self._load()

    def _load(self) -> None:
        for line in self.log_file.read_text(encoding="utf-8").splitlines():
            if line.strip():
                self.events.append(AuditEvent(**json.loads(line)))

    @staticmethod
    def fingerprint(request: dict[str, Any]) -> str:
        return hashlib.sha256(_canonical(request)).hexdigest()

    def append(self, event: AuditEvent) -> AuditEvent:
        event.previous_hash = self.events[-1].event_hash if self.events else GENESIS_HASH
        event.seal()
        with self.log_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event.to_dict(), sort_keys=True) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        self.events.append(event)
        return event

    def log_decision(self, request: dict[str, Any], decision: Any) -> AuditEvent:
        return self.append(
            AuditEvent(
                event_type=decision.action.value,
                actor=request.get("user") or request.get("agent_id"),
                action=request.get("operation") or request.get("trigger"),
                resource=request.get("resource") or request.get("tool") or request.get("file"),
                decision=decision.rule_name,
                reason=decision.reason,
                request_fingerprint=self.fingerprint(request),
                metadata={"decision_id": decision.decision_id},
            )
        )

    def log_allowed(self, request: dict[str, Any], decision: Any) -> AuditEvent:
        return self.log_decision(request, decision)

    def log_redaction(
        self, request: dict[str, Any], decision: Any, redacted_data: Any
    ) -> AuditEvent:
        return self.log_decision(request, decision)

    def log_escalation(self, request: dict[str, Any], decision: Any) -> AuditEvent:
        return self.log_decision(request, decision)

    def log_blocked(self, request: dict[str, Any], decision: Any) -> AuditEvent:
        return self.log_decision(request, decision)

    def verify_integrity(self) -> dict[str, Any]:
        previous = GENESIS_HASH
        for index, event in enumerate(self.events):
            expected = hashlib.sha256(_canonical(event.payload())).hexdigest()
            if event.previous_hash != previous or event.event_hash != expected:
                return {"valid": False, "events_checked": index, "failed_event_id": event.event_id}
            previous = event.event_hash
        return {"valid": True, "events_checked": len(self.events), "head_hash": previous}

    def get_events(
        self,
        event_type: str | None = None,
        user: str | None = None,
        resource: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        results = []
        for event in reversed(self.events):
            if event_type and event.event_type != event_type:
                continue
            if user and event.actor != user:
                continue
            if resource and event.resource != resource:
                continue
            results.append(event.to_dict())
            if len(results) >= limit:
                break
        return results

    def get_summary(self) -> dict[str, Any]:
        by_type: dict[str, int] = {}
        for event in self.events:
            by_type[event.event_type] = by_type.get(event.event_type, 0) + 1
        return {
            "total_events": len(self.events),
            "by_type": by_type,
            "integrity": self.verify_integrity(),
        }
