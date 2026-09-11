"""
Structural profiling of the NFHS-5 dataset.

Generates per-column statistics (types, uniques, nulls, ranges,
distribution), plus whole-dataset summaries.
"""

from __future__ import annotations

import logging
from typing import Dict, Any, List

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def dataset_dimensions(df: pd.DataFrame) -> Dict[str, Any]:
    """Basic shape and memory stats."""
    return {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "memory_bytes": int(df.memory_usage(deep=True).sum()),
        "memory_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
    }


def column_profile(df: pd.DataFrame) -> pd.DataFrame:
    """
    Per-column profile covering types, uniqueness, nulls, and basic stats.

    Returns a DataFrame indexed by column name.
    """
    records: List[Dict[str, Any]] = []

    for col in df.columns:
        s = df[col]
        rec: Dict[str, Any] = {
            "column": col,
            "dtype": str(s.dtype),
            "unique_count": int(s.nunique(dropna=True)),
            "unique_pct": round(s.nunique(dropna=True) / len(s) * 100, 2),
            "null_count": int(s.isna().sum()),
            "null_pct": round(s.isna().sum() / len(s) * 100, 2),
        }

        if pd.api.types.is_numeric_dtype(s):
            non_null = s.dropna()
            rec.update({
                "min": float(non_null.min()) if len(non_null) else None,
                "max": float(non_null.max()) if len(non_null) else None,
                "mean": round(float(non_null.mean()), 4) if len(non_null) else None,
                "median": round(float(non_null.median()), 4) if len(non_null) else None,
                "std": round(float(non_null.std()), 4) if len(non_null) else None,
                "zero_count": int((non_null == 0).sum()),
                "negative_count": int((non_null < 0).sum()),
                "inf_count": int(np.isinf(non_null).sum()),
            })
        else:
            # Object / categorical
            vc = s.value_counts(dropna=True)
            rec.update({
                "most_frequent_value": vc.index[0] if len(vc) else None,
                "most_frequent_count": int(vc.iloc[0]) if len(vc) else 0,
                "blank_string_count": int((s == "").sum()) if s.dtype == object else 0,
            })

        records.append(rec)

    return pd.DataFrame(records).set_index("column")


def numeric_quality_audit(df: pd.DataFrame) -> pd.DataFrame:
    """
    For every numeric column, detect zeros, negatives, inf, constants,
    near-constants, and suspiciously large values.
    """
    num_cols = df.select_dtypes(include="number").columns
    records = []

    for col in num_cols:
        s = df[col].dropna()
        n = len(s)
        if n == 0:
            continue

        iqr = float(s.quantile(0.75) - s.quantile(0.25))
        is_constant = s.nunique() <= 1
        is_near_constant = s.nunique() <= 3 or (iqr == 0 and not is_constant)

        records.append({
            "column": col,
            "n_valid": n,
            "zero_count": int((s == 0).sum()),
            "negative_count": int((s < 0).sum()),
            "inf_count": int(np.isinf(s).sum()),
            "is_constant": is_constant,
            "is_near_constant": is_near_constant,
            "min": float(s.min()),
            "max": float(s.max()),
            "iqr": round(iqr, 4),
            "std": round(float(s.std()), 4),
        })

    return pd.DataFrame(records).set_index("column")


def categorical_quality_audit(df: pd.DataFrame) -> pd.DataFrame:
    """
    For every object column, detect blanks, whitespace issues,
    inconsistent capitalisation, rare categories, etc.
    """
    obj_cols = df.select_dtypes(include="object").columns
    records = []

    for col in obj_cols:
        s = df[col]
        non_null = s.dropna()
        stripped = non_null.str.strip()

        has_leading_trailing_ws = int((non_null != stripped).sum())
        unique_raw = non_null.nunique()
        unique_lower = non_null.str.lower().str.strip().nunique()

        vc = non_null.value_counts()
        rare = vc[vc <= 2]

        records.append({
            "column": col,
            "unique_count": unique_raw,
            "unique_after_lower_strip": unique_lower,
            "capitalisation_inconsistencies": unique_raw - unique_lower,
            "leading_trailing_whitespace": has_leading_trailing_ws,
            "blank_strings": int((non_null == "").sum()),
            "rare_categories_count": len(rare),
            "top_3_values": ", ".join(vc.head(3).index.tolist()),
        })

    return pd.DataFrame(records).set_index("column")
