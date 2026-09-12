"""
Indicator inventory builder.

Parses column names to infer health domains and generates a structured
inventory exported to ``metadata/data_dictionary.csv``.
"""

from __future__ import annotations

import re
from typing import Dict, List

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
    col_lower = col_name.lower()
    for domain, keywords in _DOMAIN_RULES:
        for kw in keywords:
            if re.search(kw, col_lower):
                return domain
    return "unknown"


def _infer_unit(col_name: str) -> str:
    col_lower = col_name.lower()
    if "(%" in col_lower or col_lower.endswith("(%)"):
        return "percentage"
    if "per 1,000" in col_lower or "per 1000" in col_lower:
        return "ratio_per_1000"
    if "(rs.)" in col_lower:
        return "INR / Rupees"
    return "unknown"


def _clean_column_name(col_name: str) -> str:
    """Strip NFHS footnote superscripts and units like (%)."""
    c = col_name.strip()
    # Remove things like "12 (%)", "1, 16 (%)" at the end
    c = re.sub(r'\d*[\s,]*\(\%\)$', '', c).strip()
    c = re.sub(r'\(\%\)$', '', c).strip()
    c = re.sub(r'\(Rs\.\)$', '', c).strip()
    # Remove trailing numbers if they look like footnote markers
    c = re.sub(r'\d+$', '', c).strip()
    return c


def build_indicator_inventory(
    df: pd.DataFrame,
    classification: pd.DataFrame,
    coercion_report=None,
) -> pd.DataFrame:
    """
    Build a full indicator inventory with semantic metadata.
    """
    class_map = classification.set_index("column").to_dict("index")
    records = []

    for col in df.columns:
        s = df[col]
        domain = _infer_domain(col)
        unit = _infer_unit(col)
        clean_name = _clean_column_name(col)
        
        c_info = class_map.get(col, {})
        basic_role = c_info.get("basic_role", "UNKNOWN")
        indicator_type = c_info.get("indicator_type", "unknown")
        
        # low sample flag count
        low_sample_count = 0
        if coercion_report and col in coercion_report.parenthesized_counts:
            low_sample_count = coercion_report.parenthesized_counts[col]

        missing_pct = round(s.isna().sum() / len(s) * 100, 2)
        
        is_identifier = basic_role == "IDENTIFIER"
        is_metadata = basic_role == "SAMPLE_METADATA"

        rec = {
            "original_column_name": col,
            "clean_name": clean_name,
            "domain": domain,
            "subdomain": "unknown", # to be refined later or manually
            "indicator_type": indicator_type,
            "measurement_unit": unit,
            "directionality": "review_required",
            "is_contextual": c_info.get("is_contextual", False),
            "is_substantive_health": c_info.get("is_substantive_health", False),
            "is_health_system": c_info.get("is_health_system", False),
            "is_demographic": c_info.get("is_demographic", False),
            "is_socioeconomic": c_info.get("is_socioeconomic", False),
            "policy_relevance": "review_required" if not is_identifier and not is_metadata else "N/A",
            "missingness_rate": missing_pct,
            "low_sample_value_count": low_sample_count,
            "clustering_candidate": "review_required" if not is_identifier and not is_metadata else False,
            "holdout_candidate": "review_required" if not is_identifier and not is_metadata else False,
            "exclusion_reason": "N/A",
            "review_status": "pending",
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

        records.append(rec)

    return pd.DataFrame(records)
