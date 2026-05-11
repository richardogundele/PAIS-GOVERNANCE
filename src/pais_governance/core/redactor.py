"""
PAIS Redaction Engine

Detects and redacts personally identifiable information (PII) in spreadsheets
and other documents. Supports multiple redaction strategies.
"""

import re
import hashlib
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime
import pandas as pd
import numpy as np
from pathlib import Path

import spacy
from spacy.tokens import Doc

import logging

logger = logging.getLogger(__name__)


class PIIDetector:
    """Detects personally identifiable information using NER and patterns."""

    def __init__(self):
        """Initialize PII detector with spaCy model."""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning(
                "spaCy model not found. Install with: "
                "python -m spacy download en_core_web_sm"
            )
            self.nlp = None

    def detect_in_text(self, text: str) -> List[Tuple[str, str]]:
        """
        Detect PII entities in text using NER.

        Args:
            text: Input text to scan

        Returns:
            List of (entity, entity_type) tuples
        """
        if not self.nlp:
            return []

        doc = self.nlp(text)
        pii = []

        for ent in doc.ents:
            # PII entity types
            if ent.label_ in ["PERSON", "ORG", "GPE", "PRODUCT"]:
                pii.append((ent.text, ent.label_))

        return pii

    def detect_patterns(self, text: str) -> Dict[str, List[str]]:
        """
        Detect PII using regex patterns.

        Args:
            text: Input text to scan

        Returns:
            Dict mapping pattern type to matched values
        """
        text = str(text)
        findings = {}

        # Email pattern
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        emails = re.findall(email_pattern, text)
        if emails:
            findings["email"] = emails

        # UK phone pattern
        phone_pattern = r"\b(?:\+?44|0)(?:\d{4}|\d{3}|\d{2})?\s?\d{3,4}\s?\d{3,4}\b"
        phones = re.findall(phone_pattern, text)
        if phones:
            findings["phone"] = phones

        # SSN/ID pattern (simple: 3-digit 2-digit 4-digit)
        ssn_pattern = r"\b\d{3}-\d{2}-\d{4}\b"
        ssns = re.findall(ssn_pattern, text)
        if ssns:
            findings["ssn"] = ssns

        # Date of birth pattern (DD/MM/YYYY or DD-MM-YYYY)
        dob_pattern = r"\b(0[1-9]|[12][0-9]|3[01])[/-](0[1-9]|1[012])[/-](19|20)\d{2}\b"
        dobs = re.findall(dob_pattern, text)
        if dobs:
            findings["dob"] = [f"{m[0]}/{m[1]}/{m[2]}" for m in dobs]

        return findings

    def is_sensitive(
        self,
        text: str,
        sensitive_keywords: Optional[List[str]] = None,
    ) -> bool:
        """
        Check if text contains sensitive information.

        Args:
            text: Text to check
            sensitive_keywords: Keywords indicating sensitivity

        Returns:
            True if text appears to contain PII
        """
        text_lower = str(text).lower()

        # Check for sensitive keywords
        if sensitive_keywords:
            for keyword in sensitive_keywords:
                if keyword.lower() in text_lower:
                    return True

        # Check for patterns
        patterns = self.detect_patterns(text)
        if patterns:
            return True

        # Check for NER entities
        entities = self.detect_in_text(text)
        if entities:
            return True

        return False


class RedactionStrategy:
    """Base class for redaction strategies."""

    def redact(self, value: Any) -> str:
        """Redact a value. Override in subclasses."""
        raise NotImplementedError


class BlankRedaction(RedactionStrategy):
    """Replace with [REDACTED] marker."""

    def redact(self, value: Any) -> str:
        """Replace with blank marker."""
        return "[REDACTED]"


class TokenRedaction(RedactionStrategy):
    """Replace with deterministic token."""

    def __init__(self, salt: str = "pais-governance"):
        """Initialize with salt for hashing."""
        self.salt = salt

    def redact(self, value: Any) -> str:
        """Replace with token."""
        value_str = str(value)
        hashed = hashlib.sha256(f"{value_str}{self.salt}".encode()).hexdigest()[:12]
        return f"TOKEN_{hashed}"


class HashRedaction(RedactionStrategy):
    """Replace with hash value."""

    def redact(self, value: Any) -> str:
        """Replace with hash."""
        value_str = str(value)
        hashed = hashlib.sha256(value_str.encode()).hexdigest()[:16]
        return f"HASH_{hashed}"


class PartialRedaction(RedactionStrategy):
    """Show first/last N characters."""

    def __init__(self, show_first: int = 2, show_last: int = 2):
        """Initialize with character counts."""
        self.show_first = show_first
        self.show_last = show_last

    def redact(self, value: Any) -> str:
        """Show only first and last characters."""
        value_str = str(value)
        if len(value_str) <= self.show_first + self.show_last:
            return "*" * len(value_str)

        first = value_str[: self.show_first]
        last = value_str[-self.show_last :]
        middle = "*" * (len(value_str) - self.show_first - self.show_last)
        return f"{first}{middle}{last}"


class SpreadsheetRedactor:
    """
    Redacts sensitive information from spreadsheets.

    Example:
        >>> config = {
        ...     'sensitive_columns': ['Grade', 'Email', 'Name'],
        ...     'redaction_strategy': 'blank'
        ... }
        >>> redactor = SpreadsheetRedactor(config)
        >>> result = redactor.redact_file('grades.xlsx', ['Grade'])
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize redactor with configuration.

        Args:
            config: Configuration dict with sensitive_columns, redaction_strategy, etc.
        """
        self.config = config
        self.pii_detector = PIIDetector()
        self.sensitive_columns = config.get("sensitive_columns", [])
        self.sensitive_patterns = config.get("sensitive_patterns", {})

        # Select redaction strategy
        strategy_name = config.get("redaction_strategy", "blank").lower()
        self.strategy: RedactionStrategy
        if strategy_name == "token":
            self.strategy = TokenRedaction()
        elif strategy_name == "hash":
            self.strategy = HashRedaction()
        elif strategy_name == "partial":
            self.strategy = PartialRedaction()
        else:
            self.strategy = BlankRedaction()

    def load_spreadsheet(self, file_path: str) -> Optional[pd.DataFrame]:
        """
        Load spreadsheet from file.

        Args:
            file_path: Path to Excel or CSV file

        Returns:
            DataFrame or None if load fails
        """
        try:
            path = Path(file_path)

            if path.suffix.lower() == ".csv":
                df = pd.read_csv(path)
            elif path.suffix.lower() in [".xlsx", ".xls"]:
                df = pd.read_excel(path)
            else:
                logger.error(f"Unsupported file format: {path.suffix}")
                return None

            logger.info(f"Loaded {len(df)} rows from {path}")
            return df

        except Exception as e:
            logger.error(f"Failed to load spreadsheet: {e}")
            return None

    def identify_sensitive_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Identify columns containing sensitive data.

        Args:
            df: DataFrame to scan

        Returns:
            List of column names with sensitive data
        """
        sensitive = []

        for col in df.columns:
            col_lower = col.lower()

            # Match against configured sensitive columns
            for pattern in self.sensitive_columns:
                if pattern.lower() in col_lower:
                    sensitive.append(col)
                    logger.debug(f"Sensitive column detected: {col}")
                    break

        return sensitive

    def redact_dataframe(
        self, df: pd.DataFrame, sensitive_cols: List[str]
    ) -> Tuple[pd.DataFrame, Dict[str, int]]:
        """
        Redact sensitive columns in DataFrame.

        Args:
            df: DataFrame to redact
            sensitive_cols: Columns to redact

        Returns:
            (redacted DataFrame, statistics dict)
        """
        df_redacted = df.copy()
        stats = {col: 0 for col in sensitive_cols}

        for col in sensitive_cols:
            if col in df_redacted.columns:
                df_redacted[col] = df_redacted[col].astype(object)
                for idx, value in enumerate(df_redacted[col]):
                    if pd.notna(value):  # Skip NaN values
                        df_redacted.at[idx, col] = self.strategy.redact(value)
                        stats[col] += 1

        return df_redacted, stats

    def save_spreadsheet(self, df: pd.DataFrame, output_path: str) -> bool:
        """
        Save redacted spreadsheet to file.

        Args:
            df: DataFrame to save
            output_path: Output file path

        Returns:
            True if successful
        """
        try:
            out = Path(output_path)

            if out.suffix.lower() == ".csv":
                df.to_csv(out, index=False)
            else:
                df.to_excel(out, index=False)

            logger.info(f"Saved redacted file: {out}")
            return True

        except Exception as e:
            logger.error(f"Failed to save spreadsheet: {e}")
            return False

    def process_file(
        self,
        file_path: str,
        sensitive_columns: Optional[List[str]] = None,
        output_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process file: detect, redact, and save.

        Args:
            file_path: Input file path
            sensitive_columns: Columns to redact (if None, auto-detect)
            output_path: Output file path (if None, auto-generate)

        Returns:
            Result dict with status and details
        """
        # Load file
        df = self.load_spreadsheet(file_path)
        if df is None:
            return {
                "status": "ERROR",
                "message": "Failed to load file",
                "file": file_path,
            }

        # Identify sensitive columns
        if sensitive_columns is None:
            sensitive_columns = self.identify_sensitive_columns(df)

        if not sensitive_columns:
            logger.info(f"No sensitive columns detected in {file_path}")
            return {
                "status": "SAFE",
                "message": "No sensitive columns detected",
                "file": file_path,
                "rows": len(df),
                "total_cells_redacted": 0,
            }

        # Redact
        df_redacted, stats = self.redact_dataframe(df, sensitive_columns)

        # Save
        if output_path is None:
            file_path_obj = Path(file_path)
            redacted_name = f"{file_path_obj.stem}_REDACTED{file_path_obj.suffix}"
            output_path = str(file_path_obj.parent / redacted_name)

        success = self.save_spreadsheet(df_redacted, output_path)
        if not success:
            return {
                "status": "ERROR",
                "message": "Failed to save redacted file",
                "file": file_path,
            }

        # Return result
        total_redacted = sum(stats.values())
        return {
            "status": "REDACTED",
            "message": (
                f"Redacted {total_redacted} cells in {len(sensitive_columns)} columns"
            ),
            "original_file": file_path,
            "redacted_file": output_path,
            "sensitive_columns": sensitive_columns,
            "redaction_stats": stats,
            "total_cells_redacted": total_redacted,
            "rows": len(df),
            "timestamp": datetime.now().isoformat(),
        }


def main():
    """Example usage."""
    config = {
        "sensitive_columns": ["Student ID", "Grade", "Email", "Name"],
        "redaction_strategy": "blank",
    }

    redactor = SpreadsheetRedactor(config)
    result = redactor.process_file("sample_data.xlsx")

    print(result)


if __name__ == "__main__":
    main()
