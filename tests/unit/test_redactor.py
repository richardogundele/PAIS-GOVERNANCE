"""Unit tests for PAIS Redactor"""

import pytest
import pandas as pd
from pathlib import Path
import tempfile

from pais_governance.core.redactor import (
    SpreadsheetRedactor,
    PIIDetector,
    BlankRedaction,
    TokenRedaction,
)


@pytest.fixture
def sample_config():
    """Sample configuration."""
    return {
        "sensitive_columns": ["Grade", "Email", "Name"],
        "redaction_strategy": "blank",
    }


@pytest.fixture
def sample_dataframe():
    """Create sample DataFrame."""
    return pd.DataFrame(
        {
            "Name": ["Alice Smith", "Bob Jones"],
            "Email": ["alice@example.com", "bob@example.com"],
            "Grade": [85, 72],
            "Feedback": ["Good", "Excellent"],
        }
    )


class TestPIIDetector:
    """Test PII detection."""

    def test_detect_email(self):
        """Should detect email addresses."""
        detector = PIIDetector()
        text = "Contact alice@example.com for help"
        patterns = detector.detect_patterns(text)
        assert "email" in patterns
        assert "alice@example.com" in patterns["email"]

    def test_detect_phone(self):
        """Should detect phone numbers."""
        detector = PIIDetector()
        text = "Call me at +44 123 4567"
        patterns = detector.detect_patterns(text)
        assert "phone" in patterns

    def test_is_sensitive(self):
        """Should identify sensitive text."""
        detector = PIIDetector()
        assert detector.is_sensitive("alice@example.com")
        assert detector.is_sensitive("Alice Smith")  # NER detection
        assert not detector.is_sensitive("Hello world")


class TestRedactionStrategy:
    """Test redaction strategies."""

    def test_blank_redaction(self):
        """Blank redaction should replace with [REDACTED]."""
        strategy = BlankRedaction()
        assert strategy.redact("secret") == "[REDACTED]"
        assert strategy.redact(123) == "[REDACTED]"

    def test_token_redaction(self):
        """Token redaction should create deterministic token."""
        strategy = TokenRedaction()
        token1 = strategy.redact("alice@example.com")
        token2 = strategy.redact("alice@example.com")

        assert token1.startswith("TOKEN_")
        assert token1 == token2  # Deterministic


class TestSpreadsheetRedactor:
    """Test spreadsheet redaction."""

    def test_load_spreadsheet(self, sample_config, sample_dataframe):
        """Should load spreadsheet from file."""
        redactor = SpreadsheetRedactor(sample_config)

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            sample_dataframe.to_excel(f.name, index=False)
            df = redactor.load_spreadsheet(f.name)
            assert df is not None
            assert len(df) == 2

    def test_identify_sensitive_columns(self, sample_config, sample_dataframe):
        """Should identify sensitive columns."""
        redactor = SpreadsheetRedactor(sample_config)
        sensitive = redactor.identify_sensitive_columns(sample_dataframe)

        assert "Name" in sensitive
        assert "Email" in sensitive
        assert "Grade" in sensitive
        assert "Feedback" not in sensitive

    def test_redact_dataframe(self, sample_config, sample_dataframe):
        """Should redact sensitive columns."""
        redactor = SpreadsheetRedactor(sample_config)
        df_redacted, stats = redactor.redact_dataframe(
            sample_dataframe, ["Name", "Email", "Grade"]
        )

        # Check redaction
        assert all(df_redacted["Name"] == "[REDACTED]")
        assert all(df_redacted["Email"] == "[REDACTED]")
        assert all(df_redacted["Grade"] == "[REDACTED]")

        # Check unredacted column
        assert list(df_redacted["Feedback"]) == ["Good", "Excellent"]

        # Check stats
        assert stats["Name"] == 2
        assert stats["Email"] == 2
        assert stats["Grade"] == 2

    def test_process_file(self, sample_config, sample_dataframe):
        """Should process file end-to-end."""
        redactor = SpreadsheetRedactor(sample_config)

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input file
            input_path = Path(tmpdir) / "test.xlsx"
            sample_dataframe.to_excel(input_path, index=False)

            # Process file
            result = redactor.process_file(input_path)

            assert result["status"] == "REDACTED"
            assert result["total_cells_redacted"] > 0
            assert Path(result["redacted_file"]).exists()

    def test_no_sensitive_data(self, sample_config):
        """Should handle files with no sensitive data."""
        redactor = SpreadsheetRedactor(sample_config)

        df = pd.DataFrame(
            {"Date": ["2025-01-01", "2025-01-02"], "Count": [10, 20]}
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "safe.xlsx"
            df.to_excel(input_path, index=False)

            result = redactor.process_file(input_path)

            assert result["status"] == "SAFE"
            assert result["total_cells_redacted"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
