"""
Missingness analysis — feature-level and district-level.

Produces counts, percentages, geographic concentration analysis,
and visualisation helpers.
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
import seaborn as sns

logger = logging.getLogger(__name__)


def feature_missingness(df: pd.DataFrame) -> pd.DataFrame:
    """Per-column missing count and percentage, sorted descending."""
    missing = df.isna().sum().rename("missing_count").to_frame()
    missing["missing_pct"] = (missing["missing_count"] / len(df) * 100).round(2)
    return missing.sort_values("missing_pct", ascending=False)


def district_missingness(
    df: pd.DataFrame,
    district_col: str,
    state_col: str,
) -> pd.DataFrame:
    """
    Per-district completeness: how many indicator columns are non-null?
    """
    # Exclude identifiers from the count
    indicator_cols = [c for c in df.columns if c not in (district_col, state_col)]
    total_indicators = len(indicator_cols)

    records = []
    for idx, row in df.iterrows():
        n_missing = int(row[indicator_cols].isna().sum())
        records.append({
            "row_index": idx,
            "district": row[district_col],
            "state": row[state_col],
            "n_indicators": total_indicators,
            "n_missing": n_missing,
            "n_present": total_indicators - n_missing,
            "completeness_pct": round(
                (total_indicators - n_missing) / total_indicators * 100, 2
            ),
        })
    return (
        pd.DataFrame(records)
        .sort_values("completeness_pct", ascending=True)
        .reset_index(drop=True)
    )


def state_level_missingness(
    dist_miss: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate missingness by state to check geographic concentration."""
    return (
        dist_miss.groupby("state")
        .agg(
            n_districts=("district", "count"),
            mean_completeness=("completeness_pct", "mean"),
            min_completeness=("completeness_pct", "min"),
            max_completeness=("completeness_pct", "max"),
            mean_missing=("n_missing", "mean"),
        )
        .round(2)
        .sort_values("mean_completeness", ascending=True)
    )


def plot_feature_missingness(
    feat_miss: pd.DataFrame,
    out_path: Optional[Path] = None,
    top_n: int = 40,
) -> None:
    """Bar chart of the top-N columns by missing percentage."""
    top = feat_miss.head(top_n)
    if top["missing_pct"].max() == 0:
        logger.info("No missing values — skipping bar chart.")
        return

    fig, ax = plt.subplots(figsize=(12, max(6, top_n * 0.3)))
    ax.barh(top.index[::-1], top["missing_pct"].values[::-1], color="#e74c3c")
    ax.set_xlabel("Missing %")
    ax.set_title("Feature-level Missingness (top columns)")
    plt.tight_layout()
    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_path, dpi=150, bbox_inches="tight")
        logger.info("Saved missingness bar chart → %s", out_path)
    plt.close(fig)


def plot_missingness_heatmap(
    df: pd.DataFrame,
    out_path: Optional[Path] = None,
    max_cols: int = 60,
) -> None:
    """
    Heatmap of missing (True/False) across rows × columns.
    Downsamples columns if too many.
    """
    num_df = df.select_dtypes(include="number")
    if num_df.shape[1] > max_cols:
        # Show columns with most missingness
        miss_order = num_df.isna().sum().sort_values(ascending=False)
        num_df = num_df[miss_order.head(max_cols).index]

    fig, ax = plt.subplots(figsize=(min(20, num_df.shape[1] * 0.35), 10))
    sns.heatmap(
        num_df.isna().astype(int),
        cbar=False,
        yticklabels=False,
        xticklabels=True,
        cmap="YlOrRd",
        ax=ax,
    )
    ax.set_title("Missingness Heatmap (1 = missing)")
    ax.set_xlabel("")
    plt.xticks(rotation=90, fontsize=6)
    plt.tight_layout()
    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_path, dpi=150, bbox_inches="tight")
        logger.info("Saved missingness heatmap → %s", out_path)
    plt.close(fig)
