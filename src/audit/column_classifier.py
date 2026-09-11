"""
Column classifier — assigns each column a preliminary role.

Roles
-----
- IDENTIFIER            : district/state name, codes
- GEOGRAPHIC_METADATA   : geographic labels not used as features
- HEALTH_INDICATOR      : candidate numeric health/nutrition variable
- SAMPLE_METADATA       : survey sample counts (households, men, women surveyed)
- STATISTICAL_METADATA  : expenditure (Rs.), sex ratios (per 1000), etc.
- POTENTIAL_DERIVED     : composite scores, wealth indices, rankings
- UNKNOWN               : cannot be classified confidently

This module does NOT make final feature-selection decisions.
"""

from __future__ import annotations

import re
from typing import Dict, List

import pandas as pd


# ── Keyword-based classification rules ─────────────────────────────────

_IDENTIFIER_PATTERNS = [
    r"district",
    r"state",
    r"^code$",
    r"^id$",
]

_SAMPLE_METADATA_PATTERNS = [
    r"number of households",
    r"number of women",
    r"number of men",
    r"number of.*interviewed",
    r"number of.*surveyed",
]

_EXPENDITURE_PATTERNS = [
    r"\(rs\.\)",
    r"expenditure",
    r"rupees",
]


def classify_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Classify every column into a preliminary role.

    Returns a DataFrame with columns: [column, role, rationale].
    """
    records: List[Dict[str, str]] = []

    for col in df.columns:
        col_lower = col.lower().strip()
        role = "UNKNOWN"
        rationale = ""

        # 1. Identifiers
        if any(re.search(p, col_lower) for p in _IDENTIFIER_PATTERNS):
            if "district" in col_lower or "state" in col_lower:
                role = "IDENTIFIER"
                rationale = "Name contains district/state keyword"

        # 2. Sample metadata
        elif any(re.search(p, col_lower) for p in _SAMPLE_METADATA_PATTERNS):
            role = "SAMPLE_METADATA"
            rationale = "Survey sample size variable"

        # 3. Expenditure (Rs.)
        elif any(re.search(p, col_lower) for p in _EXPENDITURE_PATTERNS):
            role = "STATISTICAL_METADATA"
            rationale = "Monetary expenditure in Rupees — different unit/scale"

        # 4. Sex ratio (per 1,000 males) — not a percentage
        elif "sex ratio" in col_lower:
            role = "HEALTH_INDICATOR"
            rationale = "Sex ratio (per 1,000 males) — different scale from %"

        # 5. Percentage indicator — the bulk of columns
        elif col_lower.endswith("(%)") or "(%" in col_lower:
            role = "HEALTH_INDICATOR"
            rationale = "Percentage-based health/nutrition indicator"

        # 6. Fallback for numeric columns
        elif df[col].dtype in ("float64", "int64"):
            role = "UNKNOWN"
            rationale = "Numeric column with no clear unit marker in header"

        else:
            role = "UNKNOWN"
            rationale = "Cannot classify from header alone"

        records.append({"column": col, "role": role, "rationale": rationale})

    return pd.DataFrame(records)


def get_columns_by_role(
    classification: pd.DataFrame,
    role: str,
) -> List[str]:
    """Return column names for a given role."""
    return classification.loc[
        classification["role"] == role, "column"
    ].tolist()
