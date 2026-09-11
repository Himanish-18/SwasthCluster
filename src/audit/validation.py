"""
Range validation and distribution analysis for numeric indicators.

- Percentage columns: expected 0-100
- Sex ratios: expected ~800-1200 (per 1,000 males)
- Expenditure (Rs.): expected > 0
- Distribution statistics: skewness, IQR, near-zero variance
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats as sp_stats

logger = logging.getLogger(__name__)


def range_validation(
    df: pd.DataFrame,
    classification: pd.DataFrame,
) -> pd.DataFrame:
    """
    Check numeric columns against expected ranges.

    Returns a DataFrame with columns:
        column, expected_range, observed_min, observed_max,
        n_below_min, n_above_max, action
    """
    records = []

    for _, row in classification.iterrows():
        col = row["column"]
        role = row["role"]
        if col not in df.columns or not pd.api.types.is_numeric_dtype(df[col]):
            continue

        s = df[col].dropna()
        if len(s) == 0:
            continue

        col_lower = col.lower()
        obs_min = float(s.min())
        obs_max = float(s.max())

        # Determine expected range from context
        if "(%" in col_lower or col_lower.endswith("(%)"):
            exp_min, exp_max = 0.0, 100.0
            exp_label = "0–100"
        elif "sex ratio" in col_lower:
            exp_min, exp_max = 500.0, 1500.0
            exp_label = "500–1500"
        elif "(rs.)" in col_lower:
            exp_min, exp_max = 0.0, float("inf")
            exp_label = "≥ 0"
        elif role == "SAMPLE_METADATA":
            exp_min, exp_max = 0.0, float("inf")
            exp_label = "≥ 0"
        else:
            exp_min, exp_max = float("-inf"), float("inf")
            exp_label = "any"

        n_below = int((s < exp_min).sum())
        n_above = int((s > exp_max).sum()) if exp_max != float("inf") else 0

        action = "none"
        if n_below > 0 or n_above > 0:
            action = "investigate"

        records.append({
            "column": col,
            "expected_range": exp_label,
            "observed_min": round(obs_min, 4),
            "observed_max": round(obs_max, 4),
            "n_below_min": n_below,
            "n_above_max": n_above,
            "n_suspicious": n_below + n_above,
            "action": action,
        })

    return pd.DataFrame(records)


def distribution_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute distribution statistics for all numeric columns.

    Includes: mean, median, std, min, max, IQR, skewness.
    Also flags near-zero variance and high skewness.
    """
    num_cols = df.select_dtypes(include="number").columns
    records = []

    for col in num_cols:
        s = df[col].dropna()
        n = len(s)
        if n < 3:
            continue

        q1 = float(s.quantile(0.25))
        q3 = float(s.quantile(0.75))
        iqr = q3 - q1
        skew = float(sp_stats.skew(s, nan_policy="omit"))

        records.append({
            "column": col,
            "n_valid": n,
            "mean": round(float(s.mean()), 4),
            "median": round(float(s.median()), 4),
            "std": round(float(s.std()), 4),
            "min": round(float(s.min()), 4),
            "max": round(float(s.max()), 4),
            "q1": round(q1, 4),
            "q3": round(q3, 4),
            "iqr": round(iqr, 4),
            "skewness": round(skew, 4),
            "high_skew": abs(skew) > 2.0,
            "near_zero_var": float(s.std()) < 0.01,
        })

    return pd.DataFrame(records).set_index("column")


def plot_distribution_overview(
    df: pd.DataFrame,
    out_path: Optional[Path] = None,
    max_cols: int = 20,
) -> None:
    """Box-plots of the most variable numeric columns for quick overview."""
    num_df = df.select_dtypes(include="number")
    if num_df.shape[1] == 0:
        return

    # Pick columns with highest std
    stds = num_df.std().sort_values(ascending=False)
    selected = stds.head(max_cols).index.tolist()

    fig, ax = plt.subplots(figsize=(14, max(6, len(selected) * 0.4)))
    num_df[selected].boxplot(vert=False, ax=ax)
    ax.set_title(f"Distribution overview (top {max_cols} by std)")
    plt.tight_layout()
    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_path, dpi=150, bbox_inches="tight")
        logger.info("Saved distribution overview → %s", out_path)
    plt.close(fig)
