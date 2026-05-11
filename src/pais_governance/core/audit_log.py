"""
PAIS Audit Logger

Immutable audit trails for all policy decisions and data redactions.
Essential for compliance (GDPR, FERPA, etc.).
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)


class AuditEvent:
    """Single audit event."""
    
    def __init__(
        self,
        event_type: str,
        user: Optional[str] = None,
        action: Optional[str] = None,
        resource: Optional[str] = None,
        decision: Optional[str] = None,
        reason: Optional[str] = None,
        sensitive_data_detected: Optional[List[str]] = None,
        cells_redacted: int = 0
    ):
        """Initialize audit event."""
        self.timestamp = datetime.utcnow().isoformat()
        self.event_type = event_type
        self.user = user
        self.action = action
        self.resource = resource
        self.decision = decision
        self.reason = reason
        self.sensitive_data_detected = sensitive_data_detected or []
        self.cells_redacted = cells_redacted
        self.event_id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate deterministic event ID."""
        content = f"{self.timestamp}{self.event_type}{self.resource}".encode()
        return hashlib.sha256(content).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        """Export to dict."""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "user": self.user,
            "action": self.action,
            "resource": self.resource,
            "decision": self.decision,
            "reason": self.reason,
            "sensitive_data_detected": self.sensitive_data_detected,
            "cells_redacted": self.cells_redacted
        }


class AuditLogger:
    """
    Log audit events for compliance.
    
    Maintains immutable record of:
    - Policy decisions
    - Data redactions
    - Human escalations
    - Blocked actions
    """
    
    def __init__(self, log_file: Optional[str] = None):
        """
        Initialize audit logger.
        
        Args:
            log_file: Path to audit log file (JSONL format)
        """
        self.log_file = log_file or "audit.log"
        self.events: List[AuditEvent] = []
        self._ensure_log_file()
    
    def _ensure_log_file(self) -> None:
        """Ensure log file exists."""
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)
        Path(self.log_file).touch(exist_ok=True)
    
    def _append_event(self, event: AuditEvent) -> None:
        """Append event to log (immutable)."""
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(event.to_dict()) + '\n')
            self.events.append(event)
            logger.debug(f"Logged event: {event.event_id}")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def log_allowed(self, request: Dict[str, Any], decision) -> None:
        """Log allowed action."""
        event = AuditEvent(
            event_type="ALLOWED",
            user=request.get("user") or request.get("shared_by"),
            action=request.get("trigger"),
            resource=request.get("file") or request.get("resource"),
            decision=decision.rule_name,
            reason=decision.reason
        )
        self._append_event(event)
    
    def log_redaction(
        self,
        request: Dict[str, Any],
        decision,
        redacted_data: Any
    ) -> None:
        """Log data redaction."""
        event = AuditEvent(
            event_type="REDACTED",
            user=request.get("user") or request.get("shared_by"),
            action=request.get("trigger"),
            resource=request.get("file") or request.get("resource"),
            decision=decision.rule_name,
            reason=decision.reason,
            sensitive_data_detected=decision.sensitive_columns,
            cells_redacted=self._count_redactions(redacted_data)
        )
        self._append_event(event)
    
    def log_escalation(self, request: Dict[str, Any], decision) -> None:
        """Log escalation for human review."""
        event = AuditEvent(
            event_type="ESCALATED",
            user=request.get("user") or request.get("shared_by"),
            action=request.get("trigger"),
            resource=request.get("file") or request.get("resource"),
            decision=decision.rule_name,
            reason=f"Requires approval from: {', '.join(decision.approval_required_from or [])}",
            sensitive_data_detected=decision.sensitive_columns
        )
        self._append_event(event)
    
    def log_blocked(self, request: Dict[str, Any], decision) -> None:
        """Log blocked action."""
        event = AuditEvent(
            event_type="BLOCKED",
            user=request.get("user") or request.get("shared_by"),
            action=request.get("trigger"),
            resource=request.get("file") or request.get("resource"),
            decision=decision.rule_name,
            reason=decision.reason,
            sensitive_data_detected=decision.sensitive_columns
        )
        self._append_event(event)
    
    def log_decision(self, request: Dict[str, Any], decision) -> None:
        """Log policy decision."""
        event = AuditEvent(
            event_type="DECISION",
            user=request.get("user") or request.get("shared_by"),
            action=request.get("trigger"),
            resource=request.get("file") or request.get("resource"),
            decision=decision.rule_name,
            reason=decision.reason
        )
        self._append_event(event)
    
    def log_approval(
        self,
        user: str,
        resource: str,
        approved_by: str,
        reason: str = None
    ) -> None:
        """Log approval of previously escalated request."""
        event = AuditEvent(
            event_type="APPROVED",
            user=user,
            action="approval",
            resource=resource,
            decision="APPROVED",
            reason=f"Approved by {approved_by}: {reason}"
        )
        self._append_event(event)
    
    def log_denial(
        self,
        user: str,
        resource: str,
        denied_by: str,
        reason: str = None
    ) -> None:
        """Log denial of previously escalated request."""
        event = AuditEvent(
            event_type="DENIED",
            user=user,
            action="approval",
            resource=resource,
            decision="DENIED",
            reason=f"Denied by {denied_by}: {reason}"
        )
        self._append_event(event)
    
    def get_events(
        self,
        event_type: Optional[str] = None,
        user: Optional[str] = None,
        resource: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Query audit log.
        
        Args:
            event_type: Filter by event type
            user: Filter by user
            resource: Filter by resource
            limit: Max events to return
            
        Returns:
            List of matching events
        """
        results = []
        
        for event in reversed(self.events[-limit:]):
            if event_type and event.event_type != event_type:
                continue
            if user and event.user != user:
                continue
            if resource and event.resource != resource:
                continue
            
            results.append(event.to_dict())
        
        return results
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        summary = {
            "total_events": len(self.events),
            "by_type": {},
            "by_decision": {}
        }
        
        for event in self.events:
            # By type
            event_type = event.event_type
            summary["by_type"][event_type] = summary["by_type"].get(event_type, 0) + 1
            
            # By decision
            if event.decision:
                decision = event.decision
                summary["by_decision"][decision] = summary["by_decision"].get(decision, 0) + 1
        
        return summary
    
    def _count_redactions(self, redacted_data: Any) -> int:
        """Count number of redactions in data."""
        if not redacted_data:
            return 0
        
        # If DataFrame
        if hasattr(redacted_data, 'values'):
            import numpy as np
            return np.sum(redacted_data == "[REDACTED]").sum()
        
        # If dict
        if isinstance(redacted_data, dict):
            count = 0
            for v in redacted_data.values():
                if v == "[REDACTED]":
                    count += 1
            return count
        
        return 0
    
    def export_json(self, output_path: str) -> bool:
        """Export audit log as JSON."""
        try:
            with open(output_path, 'w') as f:
                json.dump(
                    [event.to_dict() for event in self.events],
                    f,
                    indent=2
                )
            logger.info(f"Exported audit log to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export audit log: {e}")
            return False


def main():
    """Example usage."""
    logger_instance = AuditLogger()
    
    # Log some events
    logger_instance.log_allowed(
        {"user": "staff@example.com", "file": "grades.xlsx"},
        type('Decision', (), {'rule_name': 'default', 'reason': 'No policy matched'})()
    )
    
    # Query
    events = logger_instance.get_events()
    print(f"Total events: {len(events)}")
    
    # Summary
    summary = logger_instance.get_summary()
    print(f"Summary: {summary}")


if __name__ == "__main__":
    main()
