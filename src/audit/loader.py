"""
Safe, auditable data loader for the NFHS-5 district dataset.

Design principles:
  - Load all values as *strings* first, then perform controlled conversion.
  - Track every coercion: suppressed values (*), parenthesized low-n values,
    whitespace stripping, and conversion failures.
  - Never modify the raw CSV on disk.
  - Return a cleaned DataFrame *plus* a full coercion report so downstream
    code can audit exactly what happened.
"""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from src.config import RAW_DATASET_PATH, NFHS_SUPPRESSED_MARKER, NFHS_PAREN_PATTERN

logger = logging.getLogger(__name__)


# ── Coercion report ────────────────────────────────────────────────────

@dataclass
class CoercionReport:
    """Tracks every transformation applied during loading."""
    raw_rows: int = 0
    raw_cols: int = 0
    loaded_rows: int = 0
    loaded_cols: int = 0
    encoding_used: str = ""

    # per-column counts
    suppressed_counts: Dict[str, int] = field(default_factory=dict)
    parenthesized_counts: Dict[str, int] = field(default_factory=dict)
    whitespace_stripped_counts: Dict[str, int] = field(default_factory=dict)
    coercion_failure_counts: Dict[str, int] = field(default_factory=dict)
    coercion_failure_examples: Dict[str, List[str]] = field(default_factory=dict)

    # totals
    total_suppressed: int = 0
    total_parenthesized: int = 0
    total_whitespace_stripped: int = 0
    total_coercion_failures: int = 0

    def summary(self) -> str:
        lines = [
            "=== Coercion Report ===",
            f"Raw shape:    {self.raw_rows} rows × {self.raw_cols} cols",
            f"Loaded shape: {self.loaded_rows} rows × {self.loaded_cols} cols",
            f"Encoding:     {self.encoding_used}",
            f"Suppressed (*) values:   {self.total_suppressed}",
            f"Parenthesized values:    {self.total_parenthesized}",
            f"Whitespace stripped:     {self.total_whitespace_stripped}",
            f"Coercion failures:       {self.total_coercion_failures}",
        ]
        if self.total_coercion_failures > 0:
            lines.append("  Failure examples by column:")
            for col, examples in self.coercion_failure_examples.items():
                lines.append(f"    {col}: {examples[:5]}")
        return "\n".join(lines)


# ── Low-sample flag DataFrame ──────────────────────────────────────────

def _build_flag_matrices(
    df_raw: pd.DataFrame,
    indicator_cols: List[str],
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Build boolean DataFrames marking suppressed and parenthesized values.

    Returns (suppressed_flags, low_sample_flags) with same index/columns
    as the indicator slice.
    """
    suppressed = pd.DataFrame(False, index=df_raw.index, columns=indicator_cols)
    low_sample = pd.DataFrame(False, index=df_raw.index, columns=indicator_cols)

    for col in indicator_cols:
        series = df_raw[col].astype(str).str.strip()
        suppressed[col] = series == NFHS_SUPPRESSED_MARKER
        low_sample[col] = series.str.match(NFHS_PAREN_PATTERN, na=False)

    return suppressed, low_sample


# ── Main loader ────────────────────────────────────────────────────────

def load_raw_dataset(
    path: str | None = None,
    encoding: str = "utf-8",
) -> Tuple[pd.DataFrame, CoercionReport]:
    """
    Load the NFHS-5 CSV into a DataFrame with controlled coercion.

    Parameters
    ----------
    path : str or None
        Path to CSV.  Defaults to ``config.RAW_DATASET_PATH``.
    encoding : str
        File encoding to try first; falls back to ``latin-1`` on error.

    Returns
    -------
    df : pd.DataFrame
        Cleaned DataFrame with numeric conversion applied where possible.
        Suppressed values (*) become NaN.
        Parenthesized values have parens stripped and are converted to float.
    report : CoercionReport
        Detailed record of everything that was changed.
    """
    path = path or str(RAW_DATASET_PATH)
    report = CoercionReport()

    # --- Step 1: read everything as strings --------------------------------
    try:
        df_raw = pd.read_csv(path, dtype=str, encoding=encoding, keep_default_na=False)
        report.encoding_used = encoding
    except UnicodeDecodeError:
        df_raw = pd.read_csv(path, dtype=str, encoding="latin-1", keep_default_na=False)
        report.encoding_used = "latin-1"
        logger.warning("Fell back to latin-1 encoding.")

    report.raw_rows, report.raw_cols = df_raw.shape
    logger.info("Loaded %d rows × %d cols from %s", report.raw_rows, report.raw_cols, path)

    # Strip column names
    df_raw.columns = [c.strip() for c in df_raw.columns]

    # --- Step 2: identify column types by header ----------------------------
    id_cols = []
    indicator_cols = []
    for col in df_raw.columns:
        val_sample = df_raw[col].str.strip().head(20).tolist()
        # Heuristic: if most non-empty values are non-numeric-looking → identifier
        if col in ("District Names", "State/UT"):
            id_cols.append(col)
        else:
            indicator_cols.append(col)

    # --- Step 3: strip whitespace everywhere --------------------------------
    for col in df_raw.columns:
        original = df_raw[col].copy()
        df_raw[col] = df_raw[col].str.strip()
        n_stripped = (original != df_raw[col]).sum()
        if n_stripped > 0:
            report.whitespace_stripped_counts[col] = int(n_stripped)
            report.total_whitespace_stripped += int(n_stripped)

    # --- Step 4: controlled numeric conversion for indicator columns --------
    paren_re = re.compile(NFHS_PAREN_PATTERN)
    df = df_raw.copy()

    for col in indicator_cols:
        series = df[col].copy()
        n_suppressed = 0
        n_paren = 0
        n_fail = 0
        fail_examples: list[str] = []

        converted = pd.Series(np.nan, index=series.index, dtype=float)

        for idx, val in series.items():
            if val == "" or val == NFHS_SUPPRESSED_MARKER:
                # NaN — suppressed or blank
                if val == NFHS_SUPPRESSED_MARKER:
                    n_suppressed += 1
                continue

            # Strip parentheses (low-sample marker)
            m = paren_re.match(val)
            if m:
                val_inner = m.group(1)
                n_paren += 1
            else:
                val_inner = val

            # Remove commas (e.g. "2,278")
            val_clean = val_inner.replace(",", "")

            try:
                converted[idx] = float(val_clean)
            except (ValueError, TypeError):
                n_fail += 1
                if len(fail_examples) < 10:
                    fail_examples.append(val)

        df[col] = converted

        if n_suppressed:
            report.suppressed_counts[col] = n_suppressed
            report.total_suppressed += n_suppressed
        if n_paren:
            report.parenthesized_counts[col] = n_paren
            report.total_parenthesized += n_paren
        if n_fail:
            report.coercion_failure_counts[col] = n_fail
            report.coercion_failure_examples[col] = fail_examples
            report.total_coercion_failures += n_fail

    report.loaded_rows, report.loaded_cols = df.shape
    logger.info(report.summary())
    return df, report


def load_raw_as_strings(
    path: str | None = None,
    encoding: str = "utf-8",
) -> pd.DataFrame:
    """Load the dataset as all-string columns, with no coercion at all."""
    path = path or str(RAW_DATASET_PATH)
    try:
        df = pd.read_csv(path, dtype=str, encoding=encoding, keep_default_na=False)
    except UnicodeDecodeError:
        df = pd.read_csv(path, dtype=str, encoding="latin-1", keep_default_na=False)
    df.columns = [c.strip() for c in df.columns]
    return df
