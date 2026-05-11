"""
PAIS Policy Gateway

Main entry point for policy enforcement.
Coordinates redaction, policy decisions, and audit logging.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging

from pais_governance.core.policy_engine import PolicyEngine, PolicyAction
from pais_governance.core.redactor import SpreadsheetRedactor
from pais_governance.core.audit_log import AuditLogger

logger = logging.getLogger(__name__)


class PolicyGateway:
    """
    Main gateway for enforcing data protection policies.

    Coordinates:
    - Policy evaluation
    - Data redaction
    - Audit logging
    - Human escalation
    """

    def __init__(
        self, config: Dict[str, Any], audit_logger: Optional[AuditLogger] = None
    ):
        """
        Initialize gateway.

        Args:
            config: Configuration dict
            audit_logger: Optional custom audit logger
        """
        self.config = config
        self.policy_engine = PolicyEngine(config.get("rules"))
        self.redactor = SpreadsheetRedactor(config)
        self.audit_logger = audit_logger or AuditLogger()

    @classmethod
    def from_config_file(cls, config_path: str) -> "PolicyGateway":
        """
        Create gateway from config file.

        Args:
            config_path: Path to pais_config.yaml

        Returns:
            Configured PolicyGateway
        """
        import yaml

        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        return cls(config)

    def enforce_policy(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enforce policy on a request.

        Args:
            request: Request dict with trigger, file, user, data, etc.

        Returns:
            Decision dict with action, safe_data, message, etc.
        """
        logger.info(f"Enforcing policy for: {request.get('trigger')}")

        # Get policy decision
        decision = self.policy_engine.evaluate(request)
        logger.info(f"Policy decision: {decision.action.value}")

        # Execute action
        if decision.action == PolicyAction.ALLOW:
            self.audit_logger.log_allowed(request, decision)
            return {
                "action": "ALLOW",
                "decision": decision.rule_name,
                "reason": decision.reason,
                "safe_data": request.get("data"),
                "timestamp": datetime.now().isoformat(),
            }

        elif decision.action == PolicyAction.LOG_FOR_AUDIT:
            self.audit_logger.log_decision(request, decision)
            return {
                "action": "LOG_FOR_AUDIT",
                "decision": decision.rule_name,
                "reason": decision.reason,
                "timestamp": datetime.now().isoformat(),
            }

        elif decision.action == PolicyAction.WARN_AND_REDACT:
            # Redact the data
            redacted_data = self._redact_data(request, decision)
            self.audit_logger.log_redaction(request, decision, redacted_data)

            return {
                "action": "WARN_AND_REDACT",
                "decision": decision.rule_name,
                "reason": decision.reason,
                "original_data": request.get("data"),
                "safe_data": redacted_data,
                "sensitive_columns": decision.sensitive_columns,
                "message": (
                    "Sensitive data detected in "
                    f"{decision.sensitive_columns}. "
                    "Redacted version provided."
                ),
                "timestamp": datetime.now().isoformat(),
            }

        elif decision.action == PolicyAction.REQUIRE_HUMAN_REVIEW:
            # Escalate to human
            self.audit_logger.log_escalation(request, decision)

            return {
                "action": "REQUIRE_HUMAN_REVIEW",
                "decision": decision.rule_name,
                "reason": decision.reason,
                "approval_required_from": decision.approval_required_from,
                "escalation_timeout_hours": decision.escalation_timeout_hours,
                "message": (
                    "This request requires approval from: "
                    f"{', '.join(decision.approval_required_from or [])}"
                ),
                "timestamp": datetime.now().isoformat(),
            }

        elif decision.action == PolicyAction.BLOCK_ACTION:
            # Block the request
            self.audit_logger.log_blocked(request, decision)

            return {
                "action": "BLOCK_ACTION",
                "decision": decision.rule_name,
                "reason": decision.reason,
                "message": f"This action is not allowed: {decision.reason}",
                "timestamp": datetime.now().isoformat(),
            }

        else:
            logger.warning(f"Unknown action: {decision.action}")
            return {
                "action": "ERROR",
                "message": f"Unknown policy action: {decision.action}",
                "timestamp": datetime.now().isoformat(),
            }

    def _redact_data(self, request: Dict[str, Any], decision) -> Dict[str, Any]:
        """
        Redact sensitive data in request.

        Args:
            request: Original request
            decision: Policy decision

        Returns:
            Redacted data
        """
        data = request.get("data")

        if not data:
            return data

        # If data is a DataFrame or dict-like
        if hasattr(data, "copy"):
            data_copy = data.copy()
            for col in decision.sensitive_columns:
                if col in data_copy.columns:
                    data_copy[col] = data_copy[col].apply(
                        self.redactor.strategy.redact
                    )
            return data_copy

        # If data is a dict
        if isinstance(data, dict):
            data_copy = data.copy()
            for col in decision.sensitive_columns:
                if col in data_copy:
                    data_copy[col] = self.redactor.strategy.redact(
                        data_copy[col]
                    )
            return data_copy

        # Otherwise return as-is
        return data

    def handle_file_share(
        self, file_path: str, shared_by: str, shared_with: str, is_external: bool = True
    ) -> Dict[str, Any]:
        """
        Handle file sharing request.

        Args:
            file_path: Path to file being shared
            shared_by: User sharing the file
            shared_with: Recipient/domain
            is_external: Whether recipient is external

        Returns:
            Decision dict
        """
        request = {
            "trigger": (
                "file_shared_externally" if is_external else "file_shared_internally"
            ),
            "file": file_path,
            "shared_by": shared_by,
            "shared_with": shared_with,
            "is_external": is_external,
        }

        return self.enforce_policy(request)

    def handle_ai_upload(
        self, file_path: str, user: str, destination: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle upload to AI tool.

        Args:
            file_path: File being uploaded
            user: User uploading
            destination: AI tool (ChatGPT, Claude, etc.)
            data: File data/contents

        Returns:
            Decision dict
        """
        request = {
            "trigger": "data_uploaded_to_ai",
            "file": file_path,
            "user": user,
            "destination": destination,
            "data": data,
        }

        return self.enforce_policy(request)


def main():
    """Example usage."""
    config = {
        "sensitive_columns": ["Grade", "Email", "Name"],
        "redaction_strategy": "blank",
        "rules": [],
    }

    gateway = PolicyGateway(config)

    # Test file sharing
    decision = gateway.handle_file_share(
        file_path="grades.xlsx",
        shared_by="staff@example.com",
        shared_with="external.com",
        is_external=True,
    )

    print(f"Decision: {decision['action']}")
    print(f"Reason: {decision['reason']}")


if __name__ == "__main__":
    main()
