"""
PAIS Policy Engine

Defines and enforces data protection policies using configurable rules.
Supports policy-as-code approach with YAML/JSON configuration.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import yaml
import json
import logging

logger = logging.getLogger(__name__)


class PolicyAction(Enum):
    """Policy decision actions."""
    ALLOW = "ALLOW"
    LOG_FOR_AUDIT = "LOG_FOR_AUDIT"
    REQUIRE_HUMAN_REVIEW = "REQUIRE_HUMAN_REVIEW"
    BLOCK_ACTION = "BLOCK_ACTION"
    WARN_AND_REDACT = "WARN_AND_REDACT"


@dataclass
class PolicyRule:
    """Single policy rule with conditions and actions."""
    
    name: str
    trigger: str  # Event type: file_shared_externally, data_uploaded_to_ai, etc.
    action: PolicyAction
    sensitive_columns: List[str] = field(default_factory=list)
    condition: Optional[Dict[str, Any]] = None
    approval_required_from: Optional[List[str]] = None
    escalation_timeout_hours: int = 24
    enabled: bool = True
    
    def matches(self, request: Dict[str, Any]) -> bool:
        """Check if request matches this rule."""
        # Check trigger
        if request.get("trigger") != self.trigger:
            return False
        
        # Check condition if defined
        if self.condition:
            for key, expected_value in self.condition.items():
                actual_value = request.get(key)
                if actual_value != expected_value:
                    return False
        
        return True


@dataclass
class PolicyDecision:
    """Result of policy evaluation."""
    
    action: PolicyAction
    rule_name: str
    reason: str
    sensitive_columns: List[str] = field(default_factory=list)
    approval_required_from: Optional[List[str]] = None
    escalation_timeout_hours: int = 24
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class PolicyEngine:
    """
    Evaluates requests against policies and makes decisions.
    
    Example:
        >>> engine = PolicyEngine.load_config("pais_config.yaml")
        >>> decision = engine.evaluate({
        ...     "trigger": "file_shared_externally",
        ...     "file": "grades.xlsx",
        ...     "user": "staff@manchester.ac.uk"
        ... })
    """
    
    def __init__(self, rules: Optional[List[PolicyRule]] = None):
        """
        Initialize policy engine.
        
        Args:
            rules: List of policy rules
        """
        self.rules = rules or []
        logger.info(f"Initialized PolicyEngine with {len(self.rules)} rules")
    
    @classmethod
    def load_config(cls, config_path: str) -> "PolicyEngine":
        """
        Load policy configuration from YAML file.
        
        Args:
            config_path: Path to pais_config.yaml
            
        Returns:
            Configured PolicyEngine instance
        """
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            engine = cls()
            
            # Load policies
            for policy_dict in config.get('policies', []):
                rule = PolicyRule(
                    name=policy_dict['name'],
                    trigger=policy_dict['trigger'],
                    action=PolicyAction[policy_dict['action'].upper()],
                    sensitive_columns=policy_dict.get('sensitive_columns', []),
                    condition=policy_dict.get('condition'),
                    approval_required_from=policy_dict.get('approval_required_from'),
                    escalation_timeout_hours=policy_dict.get('escalation_timeout_hours', 24)
                )
                engine.add_rule(rule)
            
            logger.info(f"Loaded {len(engine.rules)} rules from {config_path}")
            return engine
        
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise
    
    def add_rule(self, rule: PolicyRule) -> None:
        """
        Add a policy rule.
        
        Args:
            rule: PolicyRule to add
        """
        self.rules.append(rule)
        logger.debug(f"Added rule: {rule.name}")
    
    def evaluate(self, request: Dict[str, Any]) -> PolicyDecision:
        """
        Evaluate request against all rules.
        
        Args:
            request: Request dict with trigger, file, user, etc.
            
        Returns:
            PolicyDecision with action and reason
        """
        logger.info(f"Evaluating request: {request.get('trigger')}")
        
        # Find matching rules
        matching_rules = [rule for rule in self.rules if rule.enabled and rule.matches(request)]
        
        if not matching_rules:
            logger.info("No matching rules found, allowing by default")
            return PolicyDecision(
                action=PolicyAction.ALLOW,
                rule_name="default",
                reason="No policies matched this request"
            )
        
        # Use first matching rule
        rule = matching_rules[0]
        logger.info(f"Matched rule: {rule.name} -> {rule.action.value}")
        
        return PolicyDecision(
            action=rule.action,
            rule_name=rule.name,
            reason=f"Matched policy rule: {rule.name}",
            sensitive_columns=rule.sensitive_columns,
            approval_required_from=rule.approval_required_from,
            escalation_timeout_hours=rule.escalation_timeout_hours
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Export rules as dict."""
        return {
            "rules": [
                {
                    "name": rule.name,
                    "trigger": rule.trigger,
                    "action": rule.action.value,
                    "sensitive_columns": rule.sensitive_columns,
                    "condition": rule.condition,
                    "approval_required_from": rule.approval_required_from,
                    "enabled": rule.enabled
                }
                for rule in self.rules
            ]
        }
    
    def export_yaml(self, output_path: str) -> bool:
        """Export rules as YAML."""
        try:
            with open(output_path, 'w') as f:
                yaml.dump(self.to_dict(), f, default_flow_style=False)
            logger.info(f"Exported rules to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export rules: {e}")
            return False


class PolicyBuilder:
    """Helper to build policies programmatically."""
    
    def __init__(self):
        """Initialize builder."""
        self.rules: List[PolicyRule] = []
    
    def add_rule(
        self,
        name: str,
        trigger: str,
        action: str,
        sensitive_columns: Optional[List[str]] = None,
        condition: Optional[Dict[str, Any]] = None
    ) -> "PolicyBuilder":
        """Add a rule."""
        rule = PolicyRule(
            name=name,
            trigger=trigger,
            action=PolicyAction[action.upper()],
            sensitive_columns=sensitive_columns or [],
            condition=condition
        )
        self.rules.append(rule)
        return self
    
    def build(self) -> PolicyEngine:
        """Build PolicyEngine."""
        return PolicyEngine(self.rules)


def create_default_policies() -> List[PolicyRule]:
    """Create default policy set."""
    return [
        PolicyRule(
            name="protect_student_grades",
            trigger="file_shared_externally",
            action=PolicyAction.WARN_AND_REDACT,
            sensitive_columns=["Grade", "Student ID", "Feedback"]
        ),
        PolicyRule(
            name="protect_research_data",
            trigger="data_uploaded_to_ai",
            action=PolicyAction.REQUIRE_HUMAN_REVIEW,
            sensitive_columns=["Name", "Email", "Institution"]
        ),
        PolicyRule(
            name="allow_internal_sharing",
            trigger="file_shared_internally",
            action=PolicyAction.ALLOW
        ),
    ]


def main():
    """Example usage."""
    # Create engine with default policies
    engine = PolicyEngine(create_default_policies())
    
    # Test evaluation
    request = {
        "trigger": "file_shared_externally",
        "file": "grades.xlsx",
        "user": "staff@example.com"
    }
    
    decision = engine.evaluate(request)
    print(f"Decision: {decision.action.value}")
    print(f"Reason: {decision.reason}")


if __name__ == "__main__":
    main()
