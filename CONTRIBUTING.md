# Contributing to PAIS

PAIS welcomes small, evidence-led changes. Please open an issue before a large architectural change so the problem and interface can be agreed first.

## Development

```bash
git clone https://github.com/richardogundele/PAIS-GOVERNANCE.git
cd PAIS-GOVERNANCE
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
ruff check src tests
pytest --cov=pais_governance
```

## Pull requests

- explain the failure mode or user need
- add or update tests for behaviour changes
- keep policy outcomes backwards compatible or call out the break
- do not include credentials, personal data or production logs
- update README, architecture or roadmap claims when behaviour changes

Maintainers will evaluate correctness, threat-boundary impact, operational failure modes and documentation accuracy. A passing test suite is necessary but not sufficient.

By participating you agree to [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
