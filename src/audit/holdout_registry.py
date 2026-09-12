"""
Holdout candidate registry.

Selects candidates for held-out validation based on rules:
- Must be a substantive health outcome.
- Must not be a derived aggregate of clustering features.
- Missingness must be reasonably low (<10%).
"""

import pandas as pd

def generate_holdout_registry(data_dict: pd.DataFrame, semantic_review: pd.DataFrame) -> pd.DataFrame:
    """Generate metadata/holdout_candidate_registry.csv"""
    merged = pd.merge(data_dict, semantic_review, left_on="original_column_name", right_on="column_name")
    records = []

    for _, row in merged.iterrows():
        col = row["original_column_name"]
        
        if row["indicator_type"] in ["identifier", "survey_metadata"]:
            continue
            
        candidate_status = "rejected"
        reason = ""
        
        # Rule 1: Missingness
        if row["missingness_rate"] > 10:
            reason = "High missingness"
        # Rule 2: Substantive outcome
        elif row["indicator_type"] not in ["health_outcome", "coverage"]:
            reason = "Not a core health outcome or coverage metric"
        # Rule 3: Circularity / Derived
        elif row["is_composite"] or "redundancy" in row["clustering_risk"]:
            reason = "Composite or redundant aggregate"
        else:
            candidate_status = "candidate"
            reason = "Meets inclusion criteria"
            
        records.append({
            "column_name": col,
            "domain": row["domain"],
            "subdomain": row["subdomain"],
            "missingness_rate": row["missingness_rate"],
            "measurement_type": row["indicator_type"],
            "policy_relevance": "high",  # assumed high for outcomes
            "redundancy_with_cluster_features": row["clustering_risk"],
            "candidate_status": candidate_status,
            "reason": reason,
            "notes": ""
        })

    return pd.DataFrame(records)
