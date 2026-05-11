FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    python -m spacy download en_core_web_sm

# Copy application code
COPY src/ /app/src/
COPY setup.py .
COPY pais_config.yaml .

# Install application
RUN pip install -e .

# Create non-root user
RUN useradd -m -u 1000 pais && chown -R pais:pais /app
USER pais

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run server
CMD ["python", "-m", "pais_governance.server"]
