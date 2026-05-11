# PAIS-Governance

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)]()
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)]()

**Enterprise-grade policy-as-code AI governance for higher education and public sector.**

PAIS-Governance automatically enforces data protection policies when sensitive information interacts with AI systems. Stop accidental exposure of student data, research files, and confidential documents.

## The Problem

```
Scenario 1: Student data exposure
  ├─ Staff analyse grades in Teams
  ├─ Someone shares the file with an external collaborator
  └─ Student names + grades are now exposed (GDPR/FERPA violation)

Scenario 2: Research data leakage
  ├─ Researcher uploads survey data (with names) to ChatGPT
  ├─ ChatGPT learns patterns from real student data
  └─ Data privacy breach + regulatory investigation

Scenario 3: Confidential document sharing
  ├─ HR uploads staff salary data to cloud storage
  ├─ Link is accidentally shared publicly
  └─ Compliance incident, reputational damage
```

## The Solution

**PAIS-Governance is a policy gateway that sits between your systems and AI tools.**

```
User action (share file, upload to AI)
    ↓
PAIS-Governance policy engine
    ├─ Identify sensitive data
    ├─ Apply configured policies
    └─ Decide: ALLOW, WARN_AND_REDACT, REQUIRE_APPROVAL, BLOCK
    ↓
Safe outcome (redacted file, notification, escalation)
```

### Key Features

- ✅ **Automatic PII Detection** — Names, IDs, emails, grades, financial data
- ✅ **Real-time Policy Enforcement** — Intercept before data leaves the boundary
- ✅ **Multiple Redaction Strategies** — Blank, token, hash, partial masking
- ✅ **Audit Trail** — Every decision logged, compliant with GDPR/FERPA
- ✅ **Human Approval Workflows** — Escalate sensitive cases to DPO/compliance
- ✅ **Multi-University Support** — Configure per organization, no code changes
- ✅ **Built for Higher Education** — Works with Teams, SharePoint, Gmail, ChatGPT
- ✅ **Open Source & Extensible** — MIT license, community-driven

## Quick Start

### Installation (5 minutes)

```bash
# Clone repository
git clone https://github.com/yourusername/pais-governance.git
cd pais-governance

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration (10 minutes)

Create `pais_config.yaml`:

```yaml
organization:
  name: "University of Manchester"
  sector: "higher_education"

sensitive_data:
  columns:
    - "Student ID"
    - "Grade"
    - "Feedback"
    - "Email"
    - "Name"
    - "DOB"
  patterns:
    email: true
    phone: true
    ssn: true

redaction:
  strategy: "blank"  # or "token", "hash"
  preserve_structure: false

policies:
  - name: "student_grades_protection"
    trigger: "file_shared_externally"
    action: "warn_and_redact"
    sensitive_columns: ["Grade", "Feedback"]
    
  - name: "dpo_escalation"
    trigger: "high_risk_data_detected"
    action: "require_approval"
    approval_team: "data-protection@manchester.ac.uk"

notification:
  email: "data-protection@manchester.ac.uk"
  teams_webhook: "https://outlook.webhook.office.com/..."
```

### Deploy Locally (30 minutes)

```bash
# Using Docker
docker-compose up -d

# Or run directly
python -m pais_governance.server
```

Visit `http://localhost:8000` to test.

## Usage Examples

### Example 1: Spreadsheet Redaction

```python
from pais_governance.core.redactor import SpreadsheetRedactor
from pais_governance.core.policy import PolicyEngine

# Initialize
config = PolicyEngine.load_config("pais_config.yaml")
redactor = SpreadsheetRedactor(config)

# Process file
result = redactor.process_file(
    file_path="grades.xlsx",
    share_type="external",  # Shared with external user
)

# Result
{
    "status": "REDACTED",
    "action": "WARN_AND_REDACT",
    "sensitive_columns": ["Grade", "Student ID", "Feedback"],
    "cells_redacted": 450,
    "redacted_file": "grades_REDACTED.xlsx",
    "message": "Sensitive data detected. Redacted version created."
}
```

### Example 2: AI Tool Integration

```python
from pais_governance.core.gateway import PolicyGateway

gateway = PolicyGateway(config)

# User wants to upload to ChatGPT
request = {
    "user": "researcher@manchester.ac.uk",
    "action": "upload_to_ai",
    "file": "survey_data.csv",
    "destination": "chatgpt",
    "data": {...}  # File contents
}

# PAIS decides
decision = gateway.enforce_policy(request)

if decision["action"] == "BLOCK":
    print(f"Upload blocked: {decision['reason']}")
    # Notify user why this is blocked
    
elif decision["action"] == "ALLOW_WITH_REDACTION":
    print(f"Uploading redacted version...")
    upload_redacted_data(decision["safe_data"])
```

### Example 3: Custom Policy

```python
from pais_governance.core.policy import PolicyRule

# Define custom rule
rule = PolicyRule(
    name="protect_research_data",
    trigger="data_contains_subject_identifiers",
    condition={
        "data_type": "research",
        "contains": ["name", "email", "institution"]
    },
    action="require_approval",
    approval_required_from=["data-protection@manchester.ac.uk"],
    escalation_timeout_hours=24
)

# Use in policy engine
engine.add_rule(rule)
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Data Sources                         │
│  Teams │ SharePoint │ Gmail │ ChatGPT │ OneDrive │ File │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ↓
        ┌───────────────────────────┐
        │  PAIS-Governance Gateway  │
        ├───────────────────────────┤
        │ ├─ Request Interceptor    │
        │ ├─ PII Detector (NER)     │
        │ ├─ Policy Engine          │
        │ ├─ Redaction Pipeline     │
        │ └─ Audit Logger           │
        └───────────┬───────────────┘
                    │
        ┌───────────┴──────────────┐
        │                          │
        ↓                          ↓
    ┌────────────┐          ┌──────────────┐
    │ Safe Data  │          │ Escalation   │
    │(Processed) │          │(DPO Review)  │
    └─────┬──────┘          └──────┬───────┘
          │                        │
          ↓                        ↓
    ┌──────────────────────────────────────┐
    │         Audit Log & Compliance       │
    │  (GDPR, FERPA, UK AI Playbook)      │
    └──────────────────────────────────────┘
```

## Components

### Core Engine

- **`pais_core/redactor.py`** — PII detection & redaction logic
- **`pais_core/policy_engine.py`** — Policy rules & decision trees
- **`pais_core/audit_log.py`** — Immutable event logging
- **`pais_core/encryption.py`** — Data protection & key management

### Integrations

- **`integrations/teams_webhook.py`** — Teams Graph API listener
- **`integrations/sharepoint.py`** — SharePoint adapter
- **`integrations/gmail.py`** — Gmail integration
- **`integrations/ai_tools.py`** — ChatGPT, Claude, Copilot support

### API & Deployment

- **`server.py`** — FastAPI server for requests
- **`models.py`** — Data models & schemas
- **`config.py`** — Configuration management

## Deployment

### Docker (Recommended)

```bash
docker-compose up -d
# Access at http://localhost:8000
```

### Azure Functions

```bash
func azure functionapp publish pais-governance-prod
```

### Kubernetes

```bash
kubectl apply -f deployment/k8s/deployment.yaml
```

See [deployment/](deployment/) for detailed guides.

## Governance & Compliance

- **GDPR** — Right to erasure, data minimization, audit trails
- **FERPA** — Student record protection
- **HIPAA** — Health information safeguards (when applicable)
- **UK AI Playbook** — Governance principles for public sector AI

See [docs/GOVERNANCE.md](docs/GOVERNANCE.md) for compliance details.

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Code of conduct
- How to report bugs
- How to submit pull requests
- Development setup

## Security

**Report security vulnerabilities privately** to: `security@pais-governance.dev`

See [SECURITY.md](SECURITY.md) for details.

## Community

- **GitHub Discussions** — Ask questions, share ideas
- **Issues** — Report bugs, request features
- **Wiki** — Community-contributed guides
- **Slack** — Join our community (link in docs)

## Roadmap

### Current (v1.0)
- [x] Spreadsheet redaction (Excel, CSV)
- [x] Teams/SharePoint integration
- [x] PII detection (names, IDs, emails, grades)
- [x] Policy engine with rule support
- [x] Audit logging

### Next (v1.1)
- [ ] PowerPoint redaction
- [ ] Custom policy DSL (define rules without code)
- [ ] Web UI for policy management
- [ ] Multi-language support
- [ ] Advanced NER models (spaCy v3+)

### Future (v2.0)
- [ ] Real-time monitoring dashboard
- [ ] Machine learning-based anomaly detection
- [ ] Integration with risk management systems
- [ ] Blockchain-based audit trails (optional)
- [ ] Federated learning for threat detection

## FAQ

**Q: Does PAIS-Governance slow down file sharing?**
A: No. Redaction takes <2 seconds for typical files. Async processing available for large files.

**Q: Can staff override redactions?**
A: Yes, with DPO approval. Set `require_approval: true` in your policy.

**Q: Is this GDPR compliant?**
A: Yes. It implements data minimization, audit trails, and retention policies required by GDPR.

**Q: Can we use this with our existing systems?**
A: Yes. PAIS-Governance is designed to integrate with Teams, SharePoint, Gmail, and standard APIs.

**Q: What if the redaction misses sensitive data?**
A: The audit log captures what was (or wasn't) redacted. DPO can review and adjust policies.

## License

MIT License. See [LICENSE](LICENSE) for details.

---

**Built by God's Diamond (Richard Ogundele)**  
**Maintained as open source for the global higher education and public sector community.**

**Get started:** [docs/INSTALLATION.md](docs/INSTALLATION.md)  
**Learn more:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)  
**Questions?** [GitHub Discussions](https://github.com/yourusername/pais-governance/discussions)
