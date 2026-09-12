"""
Semantic review of composite and derived features.

Generates `metadata/indicator_semantic_review.csv`.
Identifies raw, derived, ratio, and composite indicators.
"""

import pandas as pd
import re

def generate_semantic_review(df: pd.DataFrame, data_dict: pd.DataFrame) -> pd.DataFrame:
    """
    Produce a rigorous semantic review table for all columns.
    """
    records = []
    
    for _, row in data_dict.iterrows():
        col = row["original_column_name"]
        clean = row["clean_name"]
        role = row["indicator_type"]
        is_id = role == "identifier"
        is_metadata = role == "survey_metadata"
        
        # Default flags
        classification = "Raw/Direct Indicator"
        is_composite = False
        is_derived = False
        derivation_desc = ""
        underlying = ""
        clustering_risk = "low"
        recommended_treatment = "include"
        confidence = "medium"
        notes = ""

        lower_col = col.lower()
        
        if is_id:
            classification = "Identifier"
            recommended_treatment = "exclude"
            clustering_risk = "none"
        elif is_metadata:
            classification = "Statistical Metadata"
            recommended_treatment = "exclude"
            clustering_risk = "none"
        elif "out-of-pocket expenditure" in lower_col:
            classification = "Raw/Direct Indicator"
            recommended_treatment = "include_after_scaling"
            clustering_risk = "high (scale difference)"
            notes = "Different unit (Rs). Requires scaling."
        elif "sex ratio" in lower_col:
            classification = "Ratio/Rate"
            is_derived = True
            derivation_desc = "Females per 1,000 males"
            recommended_treatment = "include_after_scaling"
            clustering_risk = "high (scale difference)"
        elif "total unmet need" in lower_col:
            classification = "Derived Indicator"
            is_derived = True
            derivation_desc = "Sum of unmet need for spacing and limiting"
            underlying = "Unmet need for spacing, Unmet need for limiting"
            clustering_risk = "high (redundancy)"
            notes = "If included, exclude the sub-components to prevent double-counting."
        elif "fully vaccinated" in lower_col:
            classification = "Composite Score"
            is_composite = True
            derivation_desc = "Requires BCG, measles, and 3 doses of polio and DPT"
            underlying = "BCG, Polio 1-3, DPT 1-3, Measles"
            clustering_risk = "high (circularity)"
            notes = "Composite index. Including both this and the individual vaccines weights immunization too heavily."
        elif "adequate diet" in lower_col and "total" in lower_col:
            classification = "Derived Indicator"
            is_derived = True
            derivation_desc = "Combines breastfed and non-breastfed diet adequacy"
            underlying = "Breastfeeding children adequate diet, Non-breastfeeding children adequate diet"
            clustering_risk = "high (redundancy)"
        elif "any method" in lower_col or "any modern method" in lower_col:
            classification = "Derived Indicator"
            is_derived = True
            derivation_desc = "Aggregate of individual contraceptive methods"
            underlying = "Pill, IUD, Condom, Sterilization, etc."
            clustering_risk = "high (redundancy)"
            notes = "Aggregate behavioral indicator."
        elif "index" in lower_col or "score" in lower_col:
            classification = "Composite Index/Score"
            is_composite = True
            is_derived = True
            clustering_risk = "high (circularity)"
            notes = "Composite index. Baseline candidate."
        
        records.append({
            "column_name": col,
            "classification": classification,
            "is_composite": is_composite,
            "is_derived": is_derived,
            "derivation_description": derivation_desc,
            "underlying_components": underlying,
            "clustering_risk": clustering_risk,
            "recommended_treatment": recommended_treatment,
            "confidence": confidence,
            "notes": notes
        })
        
    return pd.DataFrame(records)
