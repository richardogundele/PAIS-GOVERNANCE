"""
PAIS-Governance: Enterprise-grade policy-as-code AI governance

Protect sensitive data in higher education and public sector organizations
by enforcing policy-based redaction and access controls.
"""

__version__ = "1.0.0"
__author__ = "God's Diamond (Richard Ogundele)"
__email__ = "contact@pais-governance.dev"
__license__ = "MIT"

from pais_governance.core.redactor import SpreadsheetRedactor
from pais_governance.core.policy_engine import PolicyEngine
from pais_governance.core.gateway import PolicyGateway
from pais_governance.core.audit_log import AuditLogger

__all__ = [
    "SpreadsheetRedactor",
    "PolicyEngine",
    "PolicyGateway",
    "AuditLogger",
]
