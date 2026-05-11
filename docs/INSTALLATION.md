# Installation Guide

## Quick Start (5 minutes)

### Prerequisites
- Python 3.10+
- pip or conda
- Git

### Local Installation

```bash
# Clone repository
git clone https://github.com/yourusername/pais-governance.git
cd pais-governance

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Download spaCy model
python -m spacy download en_core_web_sm

# Run tests
pytest tests/ -v
```

## Docker Installation (Recommended for Production)

### Docker Compose (All-in-One)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f pais-api

# Access at http://localhost:8000
```

### Docker Build

```bash
# Build image
docker build -t pais-governance:latest .

# Run container
docker run -d \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  -v $(pwd)/pais_config.yaml:/app/pais_config.yaml \
  pais-governance:latest
```

## Azure Deployment

### Using Azure CLI

```bash
# Create resource group
az group create --name pais-rg --location uksouth

# Create App Service Plan
az appservice plan create \
  --name pais-plan \
  --resource-group pais-rg \
  --sku B2 \
  --is-linux

# Create Web App
az webapp create \
  --name pais-governance \
  --resource-group pais-rg \
  --plan pais-plan \
  --runtime "PYTHON|3.11"

# Deploy code
az webapp deployment source config-zip \
  --resource-group pais-rg \
  --name pais-governance \
  --src deploy.zip
```

### Using Terraform

```bash
cd deployment/terraform

# Initialize
terraform init

# Plan
terraform plan -out=tfplan

# Apply
terraform apply tfplan
```

## Configuration

### 1. Copy Configuration File

```bash
cp pais_config.yaml.example pais_config.yaml
```

### 2. Edit Configuration

Edit `pais_config.yaml` for your organization:

```yaml
organization:
  name: "Your University Name"
  sector: "higher_education"

sensitive_data:
  columns:
    - "Grade"
    - "Email"
    - "Name"
```

### 3. Environment Variables

Create `.env` file:

```bash
# Encryption
ENCRYPTION_KEY=your-secret-key-here

# Azure (optional)
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret

# Teams (optional)
TEAMS_WEBHOOK_URL=https://outlook.webhook.office.com/...

# Database (optional)
DATABASE_URL=postgresql://user:pass@localhost/pais
```

## Verification

### Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### Run Tests

```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

## Development Setup

### Install Dev Dependencies

```bash
pip install -e ".[dev]"
```

### Code Quality

```bash
# Format code
black src/ tests/

# Check style
flake8 src/ tests/

# Type checking
mypy src/

# Security scanning
bandit -r src/

# All checks
make lint
```

### Running Development Server

```bash
# With auto-reload
python -m pais_governance.server --reload

# Or using Makefile
make run
```

## Troubleshooting

### spaCy Model Download Fails

```bash
# Manual download
python -m spacy download en_core_web_sm

# Or use a different model
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
```

### Import Errors

```bash
# Reinstall in development mode
pip install -e . --force-reinstall --no-deps

# Or update pip
pip install --upgrade pip setuptools wheel
```

### Docker Build Issues

```bash
# Clean build cache
docker system prune -a

# Rebuild
docker-compose build --no-cache
```

## Next Steps

- [Configuration Guide](CONFIGURATION.md) — Customize for your organization
- [Architecture Guide](ARCHITECTURE.md) — Understand the system design
- [API Reference](API.md) — Use the REST API
- [Contributing Guide](../CONTRIBUTING.md) — Help improve PAIS

## Support

- **Documentation:** See [docs/](../)
- **Issues:** [GitHub Issues](https://github.com/yourusername/pais-governance/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/pais-governance/discussions)

## License

MIT License. See [LICENSE](../LICENSE) for details.
