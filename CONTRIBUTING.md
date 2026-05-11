# Contributing to PAIS-Governance

Thank you for your interest in contributing! This document explains how.

## Code of Conduct

We're committed to providing a welcoming, inclusive community. We will not tolerate:
- Harassment, discrimination, or unwelcome contact
- Bad-faith arguments or personal attacks
- Exclusionary behavior

Report violations to: `conduct@pais-governance.dev`

## Getting Started

### 1. Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/pais-governance.git
cd pais-governance

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Check code style
black src/ tests/
flake8 src/ tests/
mypy src/
```

### 2. Project Structure

```
pais-governance/
├── src/pais_governance/
│   ├── core/              # Core redaction & policy logic
│   ├── integrations/      # Teams, SharePoint, Gmail, etc.
│   ├── models/            # Data models
│   ├── utils/             # Utilities
│   └── server.py          # FastAPI server
├── tests/
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── fixtures/          # Test data
└── docs/
    ├── INSTALLATION.md
    ├── CONFIGURATION.md
    ├── ARCHITECTURE.md
    └── API.md
```

## Contributing

### Report a Bug

1. Check if it's already reported in [Issues](https://github.com/yourusername/pais-governance/issues)
2. If not, create a new issue with:
   - **Title:** Clear, concise description
   - **Description:** What happened, what you expected
   - **Steps to reproduce:** How to trigger the bug
   - **Environment:** Python version, OS, dependencies
   - **Logs:** Any error messages or stack traces

### Request a Feature

1. Check [Issues](https://github.com/yourusername/pais-governance/issues) and [Discussions](https://github.com/yourusername/pais-governance/discussions)
2. If not discussed, create an issue with:
   - **Title:** Feature description
   - **Motivation:** Why is this needed?
   - **Use case:** How would users benefit?
   - **Implementation ideas:** (optional) How might this work?

### Submit a Pull Request

#### Step 1: Fork & Branch

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/your-username/pais-governance.git
cd pais-governance

# Create a branch
git checkout -b feature/my-feature
# or for bug fixes:
git checkout -b fix/issue-123
```

#### Step 2: Make Changes

```bash
# Edit files, add tests
# Keep commits atomic and descriptive
git add .
git commit -m "Add feature X: brief description"
```

**Commit message format:**
```
type: brief description

Longer explanation of what changed and why.

Fixes #123  (if fixing an issue)
```

**Types:** `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `ci`

#### Step 3: Code Quality

```bash
# Format code
black src/ tests/

# Check style
flake8 src/ tests/

# Type checking
mypy src/

# Run tests
pytest tests/ -v --cov=src

# All together
make lint && make test
```

#### Step 4: Push & Open PR

```bash
git push origin feature/my-feature
```

Go to GitHub and open a pull request. Include:
- **Title:** Clear description
- **Description:** What changed and why
- **Related issues:** "Fixes #123"
- **Testing:** How did you test this?
- **Breaking changes:** Any API changes?

#### Step 5: Code Review

- Maintainers will review within 1 week
- Requests for changes are normal
- Be respectful and collaborative
- Address feedback in new commits (don't force-push)

#### Step 6: Merge

Once approved, your PR will be merged and you'll be credited!

## Code Style Guide

### Python

**Follow PEP 8 with these preferences:**

```python
# Use type hints
def detect_pii(text: str) -> List[str]:
    """Detect personally identifiable information in text."""
    ...

# Docstrings: Google style
class PolicyEngine:
    """Enforce data protection policies.
    
    Args:
        config: Policy configuration dict
        
    Attributes:
        policies: List of active rules
        
    Example:
        >>> engine = PolicyEngine(config)
        >>> decision = engine.enforce(request)
    """
    
# Constants: UPPER_CASE
SENSITIVE_COLUMNS = ["Grade", "Email", "Name"]

# Private methods: _leading_underscore
def _validate_config(self, config: dict) -> bool:
    ...
```

### Testing

```python
# Test file names: test_*.py
# Test class names: TestFeatureName
# Test method names: test_specific_behavior

def test_redacts_grade_column():
    """Grade column is replaced with [REDACTED]."""
    redactor = SpreadsheetRedactor(config)
    result = redactor.redact_dataframe(df, ["Grade"])
    assert all(result["Grade"] == "[REDACTED]")

def test_preserves_non_sensitive_columns():
    """Non-sensitive columns are unchanged."""
    ...
```

### Documentation

- Write clear docstrings for all public functions/classes
- Use type hints
- Include examples in docstrings
- Update README if adding new features

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_redactor.py

# Run with coverage
pytest --cov=src

# Run only unit tests (fast)
pytest tests/unit/ -v

# Run integration tests (slower)
pytest tests/integration/ -v
```

**Coverage goal:** >80% for all code.

## Documentation

- **For users:** Update [docs/](docs/) and [README.md](README.md)
- **For developers:** Update code comments and docstrings
- **For deployment:** Update [deployment/](deployment/) guides

## Releases

We follow [Semantic Versioning](https://semver.org/):
- `1.0.0` — Major.Minor.Patch
- `1.0.1` — Patch: bug fixes
- `1.1.0` — Minor: backward-compatible features
- `2.0.0` — Major: breaking changes

**Release process:**
1. Update `CHANGELOG.md`
2. Update version in `setup.py`
3. Create git tag: `git tag v1.0.1`
4. Push tag: `git push origin v1.0.1`
5. GitHub Actions creates release

## Community

- **Questions?** Start a [Discussion](https://github.com/yourusername/pais-governance/discussions)
- **Ideas?** Open an [Issue](https://github.com/yourusername/pais-governance/issues)
- **Help others?** Answer questions in Discussions
- **Share your story?** We'd love to hear how you're using PAIS-Governance

## Maintainers

Current maintainers:
- **God's Diamond (Richard Ogundele)** — Project founder, core architecture

Become a maintainer by making consistent, high-quality contributions!

## Questions?

- **Documentation issues:** See [docs/](docs/)
- **How to use?** See [README.md](README.md)
- **Found a bug?** Open an [Issue](https://github.com/yourusername/pais-governance/issues)
- **Have an idea?** Start a [Discussion](https://github.com/yourusername/pais-governance/discussions)

Thank you for making PAIS-Governance better! 🎉
