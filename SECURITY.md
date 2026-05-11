# Security Policy

## Reporting Security Vulnerabilities

If you discover a security vulnerability in PAIS-Governance, please report it **privately** to:

**Email:** `security@pais-governance.dev`

**Do NOT open a public GitHub issue for security vulnerabilities.**

### What to Include

Please provide:
- **Description:** What is the vulnerability?
- **Impact:** How could it be exploited?
- **Steps to reproduce:** How to trigger it?
- **Affected version(s):** Which versions are vulnerable?
- **Suggested fix:** (optional) How might we fix this?

### Response Timeline

- **48 hours:** We'll acknowledge receipt
- **7 days:** We'll confirm the issue and develop a fix
- **30 days:** We'll release a patch and credit you publicly (unless you prefer anonymity)

## Security Practices

### Code Review

- All code is reviewed before merge
- Security-sensitive code gets extra scrutiny
- Dependency updates are reviewed monthly

### Dependencies

- We scan dependencies with [Bandit](https://bandit.readthedocs.io/) and [Safety](https://pyup.io/safety/)
- Vulnerable packages are patched immediately
- `requirements.txt` is pinned to specific versions

### Data Protection

- **PII is never logged** — we redact sensitive data from logs
- **Redaction is one-way** — no reversal keys stored in code
- **Encryption** — AES-256 for sensitive data at rest
- **Audit trails** — immutable, tamper-proof event logs

### Access Control

- No hardcoded credentials in code
- Secrets stored in environment variables
- API keys rotated quarterly
- DPO approval required for sensitive decisions

## Security Checklist

Before deploying PAIS-Governance, ensure:

- [ ] Configuration file has strong encryption keys
- [ ] Azure credentials are stored securely (not in code)
- [ ] Audit logs are persisted to secure storage
- [ ] Teams webhook URL is HTTPS only
- [ ] CORS is restricted to trusted domains
- [ ] Regular backups of redaction decisions are taken
- [ ] DPO has reviewed the deployment

## Vulnerability Management

### Known Issues

None currently known. See [CHANGELOG.md](CHANGELOG.md) for security fixes.

### Third-Party Vulnerabilities

If you find a vulnerable dependency:

1. Check if we're already aware: run `pip audit`
2. Report to `security@pais-governance.dev`
3. We'll update the dependency and release a patch

## Best Practices for Users

### Configuration

```yaml
# ❌ DON'T do this:
pais_config.yaml:
  encryption_key: "my-secret-key-123"  # WRONG!

# ✅ DO this instead:
pais_config.yaml:
  encryption_key: ${ENCRYPTION_KEY}    # From environment

# Then set:
export ENCRYPTION_KEY="your-key-here"
```

### Deployment

```bash
# ❌ DON'T commit secrets
git add credentials.json  # WRONG!

# ✅ DO use environment variables
export TEAMS_WEBHOOK_URL="https://..."
docker-compose up

# Or use Azure Key Vault
az keyvault secret set --vault-name pais --name webhook-url --value "..."
```

### Audit Logs

- **Review regularly:** Check audit logs monthly for suspicious activity
- **Archive safely:** Move old logs to secure cold storage
- **Monitor alerts:** Set up DPO notifications for high-risk events

## Security Incident Response

If a security incident occurs:

1. **Identify:** Determine scope and impact
2. **Contain:** Stop the breach (disable shares, revoke keys)
3. **Eradicate:** Remove attacker access
4. **Recover:** Restore to secure state
5. **Review:** Update policies to prevent recurrence
6. **Report:** Notify affected parties per GDPR/FERPA

### Notifiable Events

Report to DPO if:
- PII was exposed for >1 hour
- External user gained unauthorized access
- Redaction was bypassed
- Audit logs were tampered with
- Encryption keys were compromised

## Compliance

PAIS-Governance is designed to be compliant with:

- **GDPR** — Data protection regulation (EU/UK)
- **FERPA** — Student record protection (US)
- **HIPAA** — Health information safeguards (when applicable)
- **UK AI Playbook** — Governance principles for public sector AI

See [docs/GOVERNANCE.md](docs/GOVERNANCE.md) for compliance details.

## Security Metrics

We track:
- Time to patch vulnerabilities
- Number of security issues discovered
- Number of audits passed
- Staff training completion rate

See [SECURITY_METRICS.md](SECURITY_METRICS.md) for details.

## Questions?

If you have questions about security:
- **Vulnerabilities:** `security@pais-governance.dev`
- **General security:** GitHub Discussions
- **Compliance:** [docs/GOVERNANCE.md](docs/GOVERNANCE.md)

Thank you for helping keep PAIS-Governance secure! 🔒
