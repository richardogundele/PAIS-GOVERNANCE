#!/usr/bin/env python
"""
PAIS-Governance: Enterprise-grade policy-as-code AI governance
"""

from setuptools import setup, find_packages
import os

# Read version
version_file = os.path.join(os.path.dirname(__file__), "src", "pais_governance", "__init__.py")
version = "1.0.0"
with open(version_file) as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split('"')[1]
            break

# Read long description
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pais-governance",
    version=version,
    description="Enterprise-grade policy-as-code AI governance for higher education and public sector",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="God's Diamond (Richard Ogundele)",
    author_email="contact@pais-governance.dev",
    url="https://github.com/yourusername/pais-governance",
    license="MIT",
    python_requires=">=3.10",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Education",
        "Topic :: Security",
        "Topic :: System :: Systems Administration",
    ],
    keywords=[
        "pii-detection",
        "data-governance",
        "policy-engine",
        "gdpr",
        "ferpa",
        "higher-education",
        "public-sector",
        "ai-governance",
        "redaction",
        "compliance",
    ],
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "python-dotenv>=1.0.0",
        "pandas>=2.1.0",
        "openpyxl>=3.11.0",
        "spacy>=3.7.0",
        "cryptography>=41.0.0",
        "pyjwt>=2.8.0",
        "azure-storage-blob>=12.19.0",
        "azure-identity>=1.14.0",
        "msgraph-sdk>=1.0.0",
        "python-json-logger>=2.0.0",
        "sqlalchemy>=2.0.0",
        "pyyaml>=6.0.0",
        "requests>=2.31.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.12.0",
            "flake8>=6.1.0",
            "mypy>=1.7.0",
            "bandit>=1.7.0",
            "safety>=2.3.0",
        ],
        "azure": [
            "azure-functions>=1.18.0",
        ],
        "postgres": [
            "psycopg2-binary>=2.9.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pais-governance=pais_governance.cli:main",
        ],
    },
    project_urls={
        "Documentation": "https://github.com/yourusername/pais-governance/wiki",
        "Source": "https://github.com/yourusername/pais-governance",
        "Tracker": "https://github.com/yourusername/pais-governance/issues",
        "Funding": "https://github.com/yourusername/pais-governance",
    },
)
