"""
District identity and state-district consistency audit.

Answers the critical question: does one row = one district?
Also checks for cross-state name collisions, spelling inconsistencies, etc.
"""

from __future__ import annotations

import logging
from typing import Dict, Any, List, Tuple

import pandas as pd

logger = logging.getLogger(__name__)

# Candidate column names (case-insensitive search)
_DISTRICT_CANDIDATES = [
    "district", "district name", "district names", "dist", "dist_name",
    "district_name", "district_code",
]
_STATE_CANDIDATES = [
    "state", "state/ut", "state_ut", "state name", "state_name",
    "state_code", "state/ut name",
]


def detect_identifier_columns(
    df: pd.DataFrame,
) -> Dict[str, List[str]]:
    """
    Auto-detect district and state identifier columns by matching
    column names against known patterns.

    Returns dict with keys 'district_cols' and 'state_cols', each a list
    of matched column names.
    """
    cols_lower = {c.lower().strip(): c for c in df.columns}

    district_cols = [
        cols_lower[k] for k in _DISTRICT_CANDIDATES if k in cols_lower
    ]
    state_cols = [
        cols_lower[k] for k in _STATE_CANDIDATES if k in cols_lower
    ]

    if not district_cols:
        # fallback: any column with "district" in the name
        district_cols = [c for c in df.columns if "district" in c.lower()]
    if not state_cols:
        state_cols = [c for c in df.columns if "state" in c.lower()]

    logger.info("District columns detected: %s", district_cols)
    logger.info("State columns detected: %s", state_cols)
    return {"district_cols": district_cols, "state_cols": state_cols}


def identifier_summary(
    df: pd.DataFrame,
    col: str,
) -> Dict[str, Any]:
    """Profile a single identifier column."""
    s = df[col]
    return {
        "column": col,
        "dtype": str(s.dtype),
        "unique_count": int(s.nunique(dropna=True)),
        "null_count": int(s.isna().sum()),
        "example_values": s.dropna().unique()[:10].tolist(),
        "uniqueness_ratio": round(s.nunique(dropna=True) / len(s), 4),
    }


def district_uniqueness_audit(
    df: pd.DataFrame,
    district_col: str,
    state_col: str,
) -> Dict[str, Any]:
    """
    Core audit: is (state, district) unique per row?

    Returns a dict summarising the finding plus any multi-occurrence
    districts/duplicates.
    """
    n_rows = len(df)
    n_unique_districts = df[district_col].nunique()
    n_unique_states = df[state_col].nunique()

    combo = df.groupby([state_col, district_col]).size().reset_index(name="count")
    n_unique_combos = len(combo)
    multi = combo[combo["count"] > 1]

    # Districts that appear in multiple states
    dist_state_map = (
        df.groupby(district_col)[state_col]
        .nunique()
        .reset_index(name="n_states")
    )
    cross_state = dist_state_map[dist_state_map["n_states"] > 1]

    return {
        "n_rows": n_rows,
        "n_unique_districts": n_unique_districts,
        "n_unique_states": n_unique_states,
        "n_unique_state_district_combos": n_unique_combos,
        "one_row_per_combo": n_unique_combos == n_rows,
        "multi_occurrence_combos": multi.to_dict("records") if len(multi) else [],
        "max_rows_per_combo": int(combo["count"].max()),
        "cross_state_districts": cross_state.merge(
            df[[district_col, state_col]].drop_duplicates(),
            on=district_col,
        ).to_dict("records") if len(cross_state) else [],
        "n_cross_state_district_names": len(cross_state),
    }


def state_consistency_audit(
    df: pd.DataFrame,
    state_col: str,
) -> Dict[str, Any]:
    """
    Check for spelling/whitespace/capitalisation inconsistencies in state names.
    """
    states_raw = df[state_col].dropna().unique().tolist()
    states_stripped = [s.strip() for s in states_raw]
    states_lower = [s.lower().strip() for s in states_raw]

    # Detect near-duplicates (differ only by case or whitespace)
    seen: Dict[str, List[str]] = {}
    for raw, low in zip(states_raw, states_lower):
        seen.setdefault(low, []).append(raw)
    inconsistent = {k: v for k, v in seen.items() if len(set(v)) > 1}

    # Whitespace issues
    ws_issues = [s for s, st in zip(states_raw, states_stripped) if s != st]

    return {
        "n_unique_raw": len(set(states_raw)),
        "n_unique_normalised": len(set(states_lower)),
        "capitalisation_inconsistencies": inconsistent,
        "whitespace_issues": ws_issues,
        "all_states_sorted": sorted(set(states_stripped)),
    }


def district_consistency_audit(
    df: pd.DataFrame,
    district_col: str,
) -> Dict[str, Any]:
    """
    Check district-name quality: whitespace, empty strings, etc.
    """
    districts_raw = df[district_col].dropna().tolist()
    districts_stripped = [d.strip() for d in districts_raw]

    ws_issues = [d for d, ds in zip(districts_raw, districts_stripped) if d != ds]

    return {
        "n_unique_raw": len(set(districts_raw)),
        "n_unique_stripped": len(set(districts_stripped)),
        "whitespace_issues_count": len(ws_issues),
        "whitespace_issue_examples": ws_issues[:20],
    }


def generate_district_identity_csv(
    df: pd.DataFrame,
    district_col: str,
    state_col: str,
) -> pd.DataFrame:
    """
    Produce a per-row CSV of district identifiers suitable for export
    to ``metadata/district_identity_audit.csv``.
    """
    records = []
    for idx, row in df.iterrows():
        district = row[district_col]
        state = row[state_col]
        records.append({
            "row_index": idx,
            "district_raw": district,
            "district_stripped": district.strip() if isinstance(district, str) else district,
            "state_raw": state,
            "state_stripped": state.strip() if isinstance(state, str) else state,
            "has_whitespace_issue": (
                district != district.strip() if isinstance(district, str) else False
            ),
        })
    return pd.DataFrame(records)
