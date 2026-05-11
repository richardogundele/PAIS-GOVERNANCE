# Changelog

All notable changes to PAIS-Governance are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] — 2026-05-11

### Added

#### Core Features
- ✅ Automatic PII detection using spaCy NER and regex patterns
- ✅ Spreadsheet redaction (Excel .xlsx, CSV)
- ✅ Multiple redaction strategies: blank, token, hash, partial masking
- ✅ Policy engine with rule-based decision making
- ✅ Support for 4 policy actions: ALLOW, LOG_FOR_AUDIT, REQUIRE_HUMAN_REVIEW, BLOCK_ACTION
- ✅ Immutable audit logging for all decisions
- ✅ AES-256 encryption for sensitive data at rest
- ✅ Human approval workflows with DPO escalation

#### Integrations
- ✅ Teams/SharePoint integration via Graph API webhook
- ✅ FastAPI server for REST API requests
- ✅ Docker & Docker Compose for containerized deployment
- ✅ Terraform for Azure infrastructure as code

#### Configuration
- ✅ YAML-based configuration (per-organization)
- ✅ Environment variable support
- ✅ Multi-organization support (no code changes needed)
- ✅ Customizable sensitive column detection
- ✅ Flexible policy rule definitions

#### Compliance & Governance
- ✅ GDPR compliance (data minimization, audit trails, retention)
- ✅ FERPA compliance (student record protection)
- ✅ HIPAA-ready (when applicable)
- ✅ UK AI Playbook alignment
- ✅ Configurable data retention policies

#### Testing & Validation
- ✅ Unit test suite (80%+ coverage)
- ✅ Integration tests for Teams, SharePoint, CSV/Excel
- ✅ Sample test data (synthetic student records)
- ✅ CI/CD pipeline (GitHub Actions)
- ✅ Automated security scanning (Bandit, CodeQL)
- ✅ Code quality checks (Black, Flake8, MyPy)

#### Documentation
- ✅ Comprehensive README with quick start
- ✅ Installation guide for Docker, Azure, local development
- ✅ Configuration guide with examples
- ✅ Architecture documentation
- ✅ API reference
- ✅ Governance & compliance guide
- ✅ Security policy & vulnerability reporting
- ✅ Contributing guide
- ✅ Code of conduct

#### Deployment
- ✅ Docker Compose for local/development
- ✅ Azure Functions deployment
- ✅ Kubernetes manifests (optional)
- ✅ Environment-based configuration

### Security
- ✅ No hardcoded credentials
- ✅ Environment variable support for secrets
- ✅ Encrypted reversal keys (never in logs)
- ✅ Audit trail immutability
- ✅ Dependency vulnerability scanning
- ✅ Input validation & sanitization

### Known Limitations
- PowerPoint redaction not yet supported (planned v1.1)
- Gmail integration webhook setup requires manual configuration
- Web UI for policy management planned for v1.1
- Single-threaded redaction (async planned for v1.1)

## [Unreleased]

### Planned for v1.1
- [ ] PowerPoint & PDF redaction
- [ ] Custom policy DSL (define rules without code)
- [ ] Web UI for policy management
- [ ] Async batch processing for large files
- [ ] Advanced NER models (spaCy v3+)
- [ ] Gmail integration improvements
- [ ] Multi-language support
- [ ] Performance optimizations

### Planned for v2.0
- [ ] Real-time monitoring dashboard
- [ ] Machine learning-based anomaly detection
- [ ] Integration with risk management systems
- [ ] Blockchain-based audit trails (optional)
- [ ] Federated learning for threat detection
- [ ] Advanced de-identification techniques
- [ ] Automated compliance reporting

---

## Release Process

1. Update `CHANGELOG.md` with changes
2. Update version in `setup.py` and `src/pais_governance/__init__.py`
3. Create git tag: `git tag v1.0.1`
4. Push tag: `git push origin v1.0.1`
5. GitHub Actions creates release automatically

## Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- **Major** (1.0.0 → 2.0.0): Breaking changes
- **Minor** (1.0.0 → 1.1.0): New features (backward-compatible)
- **Patch** (1.0.0 → 1.0.1): Bug fixes

## Support Timeline

- **v1.0.x**: Supported for 12 months
- **v1.1.x**: Supported for 12 months
- **v2.0.x**: Supported for 18 months

---

**Latest Release:** [v1.0.0](https://github.com/yourusername/pais-governance/releases/tag/v1.0.0)

**Changelog Source:** [GitHub Releases](https://github.com/yourusername/pais-governance/releases)
