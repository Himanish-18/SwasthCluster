"""
Indicator inventory builder.

Parses column names to infer health domains and generates a structured
inventory exported to ``metadata/data_dictionary.csv``.

IMPORTANT: domains are *inferred* from column-name keywords.  If the
meaning of a column cannot be determined from its header, it is marked
``unknown / requires documentation``.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional

import numpy as np
import pandas as pd


# ── Domain keyword mapping ─────────────────────────────────────────────

_DOMAIN_RULES: List[tuple[str, List[str]]] = [
    ("maternal_health", [
        "antenatal", "postnatal", "delivery", "institutional birth",
        "caesarean", "neonatal tetanus", "iron folic acid", "mcp card",
        "mothers who", "registered pregnanc", "home birth",
        "skilled health personnel", "births attended",
    ]),
    ("reproductive_health", [
        "family planning", "sterilization", "iud", "ppiud", "pill",
        "condom", "injectables", "unmet need", "married before age",
        "already mothers or pregnant", "menstrual",
    ]),
    ("child_health", [
        "children under age 5", "children under 5",
        "diarrhoea", "ors", "zinc", "respiratory infection", "ari",
        "breastfed", "breastfeeding", "solid or semi-solid",
        "adequate diet", "vitamin a",
    ]),
    ("immunization", [
        "vaccinated", "vaccination", "bcg", "polio", "penta",
        "dpt", "measles", "mcv", "rotavirus", "hepatitis",
    ]),
    ("nutrition", [
        "stunted", "wasted", "severely wasted", "underweight",
        "overweight", "bmi", "body mass",
    ]),
    ("anemia", [
        "anaemic", "anemic", "anaemia", "anemia",
    ]),
    ("non_communicable_disease", [
        "blood sugar", "blood pressure", "hypertension",
        "cervical cancer", "breast cancer", "oral cancer",
        "screening", "breast examination", "oral cavity",
    ]),
    ("substance_use", [
        "tobacco", "alcohol",
    ]),
    ("household_environment", [
        "electricity", "drinking-water", "sanitation",
        "clean fuel", "iodized salt",
    ]),
    ("healthcare_access", [
        "health insurance", "health facility",
        "pre-primary school", "school year",
    ]),
    ("demographics", [
        "sex ratio", "population below age",
        "births in the 5 years.*third or higher",
    ]),
    ("literacy_education", [
        "literate", "schooling", "attended school",
    ]),
    ("registration", [
        "birth was registered", "deaths.*registered",
    ]),
    ("survey_metadata", [
        "number of households", "number of women", "number of men",
        "out-of-pocket expenditure",
    ]),
]


def _infer_domain(col_name: str) -> str:
    """Best-effort domain inference from column header text."""
    col_lower = col_name.lower()
    for domain, keywords in _DOMAIN_RULES:
        for kw in keywords:
            if re.search(kw, col_lower):
                return domain
    return "unknown"


def _infer_unit(col_name: str) -> str:
    """Infer measurement unit from column header."""
    col_lower = col_name.lower()
    if "(%" in col_lower or col_lower.endswith("(%)"):
        return "percentage"
    if "per 1,000" in col_lower or "per 1000" in col_lower:
        return "ratio_per_1000"
    if "(rs.)" in col_lower:
        return "rupees"
    return "unknown"


def build_indicator_inventory(
    df: pd.DataFrame,
    classification: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build a full indicator inventory with domain, unit, stats, and role.

    Parameters
    ----------
    df : pd.DataFrame
        The loaded (coerced) dataset.
    classification : pd.DataFrame
        Output of ``column_classifier.classify_columns``.

    Returns
    -------
    pd.DataFrame with one row per column.
    """
    class_map = dict(zip(classification["column"], classification["role"]))
    records = []

    for col in df.columns:
        s = df[col]
        domain = _infer_domain(col)
        unit = _infer_unit(col)
        role = class_map.get(col, "UNKNOWN")

        rec: Dict[str, object] = {
            "column_name": col,
            "data_type": str(s.dtype),
            "domain": domain,
            "unit": unit,
            "candidate_role": role,
            "unique_count": int(s.nunique(dropna=True)),
            "missing_count": int(s.isna().sum()),
            "missing_pct": round(s.isna().sum() / len(s) * 100, 2),
        }

        if pd.api.types.is_numeric_dtype(s):
            nn = s.dropna()
            rec.update({
                "min": round(float(nn.min()), 4) if len(nn) else None,
                "max": round(float(nn.max()), 4) if len(nn) else None,
                "mean": round(float(nn.mean()), 4) if len(nn) else None,
                "median": round(float(nn.median()), 4) if len(nn) else None,
            })
        else:
            rec.update({"min": None, "max": None, "mean": None, "median": None})

        # Notes for the reviewer
        notes_parts = []
        if domain == "unknown":
            notes_parts.append("domain could not be inferred from header")
        if unit == "unknown":
            notes_parts.append("unit could not be inferred from header")
        rec["notes"] = "; ".join(notes_parts) if notes_parts else ""

        records.append(rec)

    return pd.DataFrame(records)
