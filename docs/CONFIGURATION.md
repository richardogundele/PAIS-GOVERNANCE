# Configuration Guide

## Overview

PAIS-Governance is configured via `pais_config.yaml`. No code changes needed.

## Configuration File Structure

```yaml
organization:    # Organization metadata
sensitive_data:  # What to detect and redact
redaction:       # How to redact
policies:        # When to apply redaction
notification:    # Who to alert
audit:          # How to log events
teams:          # Teams integration (optional)
logging:        # Logging settings
api:            # API settings
security:       # Security settings
```

## Organization

```yaml
organization:
  name: "University of Manchester"
  sector: "higher_education"  # or "public_sector", "nhs", etc.
  environment: "production"    # "development", "staging", "production"
```

## Sensitive Data Detection

### Column Names

```yaml
sensitive_data:
  columns:
    - "Student ID"
    - "Grade"
    - "Feedback"
    - "Email"
    - "Name"
```

PAIS automatically detects these columns (case-insensitive). Add your own:

```yaml
sensitive_data:
  columns:
    - "Staff Salary"      # Custom column
    - "Medical Record"    # Custom column
```

### Pattern Detection

Enable automatic pattern matching:

```yaml
sensitive_data:
  patterns:
    email: true      # Detect email addresses
    phone: true      # Detect phone numbers
    ssn: true        # Detect SSN/ID numbers
    dob: true        # Detect dates of birth
```

## Redaction Strategies

### Blank Redaction (Default)

```yaml
redaction:
  strategy: "blank"
```

Result: `Alice Smith` → `[REDACTED]`

### Token Redaction

```yaml
redaction:
  strategy: "token"
```

Result: `Alice Smith` → `TOKEN_a7f2b91c`

Deterministic: same input always produces same token (good for joins).

### Hash Redaction

```yaml
redaction:
  strategy: "hash"
```

Result: `Alice Smith` → `HASH_f5a28a4c`

### Partial Redaction

```yaml
redaction:
  strategy: "partial"
  show_first: 2    # Show first 2 characters
  show_last: 2     # Show last 2 characters
```

Result: `Alice Smith` → `Al****th`

## Policies

Define when and how to apply redaction:

```yaml
policies:
  - name: "student_grades_protection"
    trigger: "file_shared_externally"
    action: "WARN_AND_REDACT"
    sensitive_columns:
      - "Grade"
      - "Student ID"
    condition:
      file_type: ["xlsx", "csv"]
```

### Triggers

- `file_shared_externally` — File shared with external user/domain
- `file_shared_internally` — File shared within organization
- `data_uploaded_to_ai` — Data sent to AI tool (ChatGPT, Claude, etc.)
- `data_accessed_by_guest` — Guest user accesses data
- `data_contains_subject_identifiers` — PII detected in file

### Actions

- `ALLOW` — Allow without redaction
- `LOG_FOR_AUDIT` — Allow but log the decision
- `WARN_AND_REDACT` — Redact data, notify user
- `REQUIRE_HUMAN_REVIEW` — Escalate for approval
- `BLOCK_ACTION` — Block completely

### Conditions (Optional)

```yaml
condition:
  file_type: ["xlsx", "csv"]           # File types
  data_type: "research"                 # Data classification
  user_department: "Finance"            # User's department
  recipient_domain: ["external.com"]    # External domains
```

### Approval Workflows

```yaml
policies:
  - name: "research_approval"
    trigger: "data_uploaded_to_ai"
    action: "REQUIRE_HUMAN_REVIEW"
    approval_required_from:
      - "data-protection@manchester.ac.uk"
      - "research-ethics@manchester.ac.uk"
    escalation_timeout_hours: 48  # Request expires in 48 hours
```

### Example Policies

**Protect all student data:**
```yaml
policies:
  - name: "protect_all_student_data"
    trigger: "file_shared_externally"
    action: "REQUIRE_HUMAN_REVIEW"
    sensitive_columns: ["Name", "Email", "Grade", "Feedback"]
    approval_required_from: ["dpo@manchester.ac.uk"]
```

**Allow internal sharing without review:**
```yaml
policies:
  - name: "allow_internal"
    trigger: "file_shared_internally"
    action: "ALLOW"
```

**Warn and redact for AI uploads:**
```yaml
policies:
  - name: "ai_safety"
    trigger: "data_uploaded_to_ai"
    action: "WARN_AND_REDACT"
    sensitive_columns: ["Name", "Email", "PersonalData"]
```

## Notifications

```yaml
notification:
  # Email for alerts
  email: "data-protection@manchester.ac.uk"
  
  # Teams webhook
  teams_webhook: "https://outlook.webhook.office.com/..."
  
  # Alert on these events
  alert_on: ["BLOCKED", "ESCALATED", "ERROR"]
```

## Audit Logging

```yaml
audit:
  # Log file location
  log_file: "logs/audit.log"
  
  # Keep logs for N days
  retention_days: 365
  
  # Optional: centralized database
  database: "postgresql://user:pass@localhost/pais_governance"
```

## Logging

```yaml
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  format: "json" # or "text"
  
  file: "logs/pais.log"
  console: true
```

## API Settings

```yaml
api:
  host: "0.0.0.0"
  port: 8000
  debug: false
  
  # CORS allowed origins
  cors_origins:
    - "http://localhost:3000"
    - "https://myapp.example.com"
```

## Security

```yaml
security:
  # Encryption key (use environment variable!)
  encryption_key: ${ENCRYPTION_KEY}
  
  # Require HTTPS in production
  require_https: true
  
  # Rate limiting
  rate_limit_per_minute: 60
  
  # API authentication
  require_api_key: true
```

## Environment Variables

Reference environment variables with `${VARIABLE_NAME}`:

```yaml
security:
  encryption_key: ${ENCRYPTION_KEY}

teams:
  client_secret: ${AZURE_CLIENT_SECRET}
```

Set in `.env`:
```bash
ENCRYPTION_KEY=your-secret-key
AZURE_CLIENT_SECRET=your-secret
```

## Per-Organization Configs

### University of Manchester

```yaml
organization:
  name: "University of Manchester"
  sector: "higher_education"

sensitive_data:
  columns:
    - "Student ID"
    - "Grade"
    - "Email"
    - "Name"

policies:
  - name: "protect_grades"
    trigger: "file_shared_externally"
    action: "WARN_AND_REDACT"
    sensitive_columns: ["Grade", "Student ID"]
```

### NHS Trust

```yaml
organization:
  name: "Example NHS Trust"
  sector: "nhs"

sensitive_data:
  columns:
    - "Patient ID"
    - "NHS Number"
    - "Medical Record"
    - "Diagnosis"
    - "Medication"

policies:
  - name: "hipaa_protection"
    trigger: "data_uploaded_to_ai"
    action: "BLOCK_ACTION"  # Never upload PHI to AI
```

### Government Department

```yaml
organization:
  name: "Example Government Dept"
  sector: "public_sector"

sensitive_data:
  columns:
    - "Citizen ID"
    - "SSN"
    - "Address"
    - "Salary"

policies:
  - name: "uk_ai_playbook_compliance"
    trigger: "data_uploaded_to_ai"
    action: "REQUIRE_HUMAN_REVIEW"
    approval_required_from: ["data-protection@govt.uk"]
```

## Validation

Validate your config:

```bash
python -m pais_governance.config --validate pais_config.yaml
```

## Troubleshooting

### Config Not Loading

```bash
# Check YAML syntax
python -m yaml pais_config.yaml

# Check file permissions
ls -la pais_config.yaml
```

### Columns Not Being Detected

- Check column names (case-insensitive matching)
- Verify spelling in both spreadsheet and config
- Enable pattern detection for emails, phones, etc.

### Policies Not Triggering

- Check trigger name matches exactly
- Verify conditions if used
- Enable debug logging to see what's happening

## Next Steps

- [Installation Guide](INSTALLATION.md) — Install PAIS
- [Architecture Guide](ARCHITECTURE.md) — How it works
- [API Reference](API.md) — Use programmatically

## Support

- **Questions?** See [Discussions](https://github.com/yourusername/pais-governance/discussions)
- **Bugs?** Open an [Issue](https://github.com/yourusername/pais-governance/issues)
