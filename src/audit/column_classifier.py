"""
Semantic column classifier — assigns each column a nuanced role and type.

This module maps raw columns to specific semantic categories rather than
just a generic "HEALTH_INDICATOR". It distinguishes between true health
outcomes, demographic context, healthcare access, and metadata.
"""

from __future__ import annotations

import re
from typing import Dict, List, Any

import pandas as pd


# ── Keyword-based semantic rules ───────────────────────────────────────

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

_OOP_EXPENDITURE_PATTERNS = [
    r"out-of-pocket expenditure",
]

_DEMOGRAPHIC_PATTERNS = [
    r"population below age",
    r"sex ratio of the total population",
    r"sex ratio at birth",
    r"births in the 5 years.*third or higher",
]

_SOCIOECONOMIC_PATTERNS = [
    r"attended school",
    r"literate",
    r"years of schooling",
    r"married before age",
    r"health insurance",  # Also access, but strongly socioeconomic context
]

_HOUSEHOLD_ENV_PATTERNS = [
    r"electricity",
    r"drinking-water",
    r"sanitation",
    r"clean fuel",
    r"iodized salt",
]

_ACCESS_SYSTEM_PATTERNS = [
    r"health facility",
    r"institutional birth",
    r"health worker ever talked",
    r"postnatal care from a doctor",
    r"births attended by skilled",
    r"received most of their vaccinations",
    r"taken to a health facility",
]


def classify_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Classify every column into a preliminary semantic role.
    
    Returns a DataFrame with columns:
    [column, basic_role, indicator_type, is_contextual, is_substantive_health, is_health_system, is_demographic, is_socioeconomic]
    """
    records: List[Dict[str, Any]] = []

    for col in df.columns:
        col_lower = col.lower().strip()
        
        # Defaults
        basic_role = "UNKNOWN"
        indicator_type = "unknown"
        is_contextual = False
        is_substantive_health = False
        is_health_system = False
        is_demographic = False
        is_socioeconomic = False
        
        # 1. Identifiers
        if any(re.search(p, col_lower) for p in _IDENTIFIER_PATTERNS) and ("district" in col_lower or "state" in col_lower):
            basic_role = "IDENTIFIER"
            indicator_type = "identifier"
            
        # 2. Sample metadata
        elif any(re.search(p, col_lower) for p in _SAMPLE_METADATA_PATTERNS):
            basic_role = "SAMPLE_METADATA"
            indicator_type = "survey_metadata"
            
        # 3. Out of pocket expenditure (Explicit correction: Health System / Access)
        elif any(re.search(p, col_lower) for p in _OOP_EXPENDITURE_PATTERNS):
            basic_role = "HEALTH_SYSTEM"
            indicator_type = "access_affordability"
            is_health_system = True
            
        # 4. Demographics
        elif any(re.search(p, col_lower) for p in _DEMOGRAPHIC_PATTERNS):
            basic_role = "CONTEXTUAL"
            indicator_type = "demographic"
            is_contextual = True
            is_demographic = True
            
        # 5. Socioeconomic / Education
        elif any(re.search(p, col_lower) for p in _SOCIOECONOMIC_PATTERNS):
            basic_role = "CONTEXTUAL"
            indicator_type = "socioeconomic"
            is_contextual = True
            is_socioeconomic = True
            
        # 6. Household Environment
        elif any(re.search(p, col_lower) for p in _HOUSEHOLD_ENV_PATTERNS):
            basic_role = "CONTEXTUAL"
            indicator_type = "household_environment"
            is_contextual = True
            
        # 7. Healthcare Access / System
        elif any(re.search(p, col_lower) for p in _ACCESS_SYSTEM_PATTERNS):
            basic_role = "HEALTH_SYSTEM"
            indicator_type = "access_utilization"
            is_health_system = True
            
        # 8. Substantive Health Outcomes / Behaviors (The rest of the % indicators)
        elif col_lower.endswith("(%)") or "(%" in col_lower:
            basic_role = "SUBSTANTIVE_HEALTH"
            is_substantive_health = True
            
            # Sub-classify outcomes vs behaviors/coverage
            if any(k in col_lower for k in ["anaemic", "stunted", "wasted", "underweight", "overweight", "bmi", "blood sugar", "blood pressure", "diarrhoea", "ari "]):
                indicator_type = "health_outcome"
            elif any(k in col_lower for k in ["vaccin", "bcg", "polio", "dpt", "measles", "rotavirus", "hepatitis", "received", "consumed iron", "check-up", "examination"]):
                indicator_type = "coverage"
            elif any(k in col_lower for k in ["use", "tobacco", "alcohol", "breastfed", "diet", "family planning", "sterilization", "pill", "condom", "iud"]):
                indicator_type = "behavior"
            else:
                indicator_type = "other_health"
                
        # 9. Fallback
        elif df[col].dtype in ("float64", "int64"):
            basic_role = "UNKNOWN"
            indicator_type = "numeric_unknown"
            
        records.append({
            "column": col,
            "basic_role": basic_role,
            "indicator_type": indicator_type,
            "is_contextual": is_contextual,
            "is_substantive_health": is_substantive_health,
            "is_health_system": is_health_system,
            "is_demographic": is_demographic,
            "is_socioeconomic": is_socioeconomic,
        })

    return pd.DataFrame(records)

def get_columns_by_role(classification: pd.DataFrame, role: str) -> List[str]:
    return classification.loc[classification["basic_role"] == role, "column"].tolist()
