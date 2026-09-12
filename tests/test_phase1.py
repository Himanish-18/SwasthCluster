"""
Phase 1 — Tests for critical data assumptions.

These tests verify behaviour of the audit modules, not merely that
code runs.  They check:
  1. Dataset loads successfully and preserves row count.
  2. District/state identifiers are detected.
  3. No silent row loss during loading.
  4. Numeric validation catches known edge cases.
  5. Missingness calculations are correct.
  6. Audit outputs are generated on a real run.
  7. Coercion tracking works as expected.
  8. Semantic logic for corrective pass.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Ensure project root on path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import RAW_DATASET_PATH
from src.audit.loader import load_raw_dataset, load_raw_as_strings
from src.audit.dataset_profile import (
    dataset_dimensions,
    column_profile,
    numeric_quality_audit,
)
from src.audit.district_audit import (
    detect_identifier_columns,
    district_uniqueness_audit,
)
from src.audit.missingness import feature_missingness, district_missingness
from src.audit.column_classifier import classify_columns, get_columns_by_role
from src.audit.indicator_inventory import build_indicator_inventory
from src.audit.validation import range_validation, distribution_statistics
from src.audit.semantic_review import generate_semantic_review
from src.audit.holdout_registry import generate_holdout_registry


# ── Fixtures ───────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def raw_strings() -> pd.DataFrame:
    """Load the dataset as all strings (no coercion)."""
    return load_raw_as_strings()


@pytest.fixture(scope="module")
def loaded():
    """Load the dataset with controlled coercion."""
    df, report = load_raw_dataset()
    return df, report


@pytest.fixture(scope="module")
def df(loaded) -> pd.DataFrame:
    return loaded[0]


@pytest.fixture(scope="module")
def coercion(loaded):
    return loaded[1]


# ── 1. Dataset loads successfully ──────────────────────────────────────

class TestDataLoading:
    def test_dataset_file_exists(self):
        assert RAW_DATASET_PATH.exists(), (
            f"Dataset not found at {RAW_DATASET_PATH}"
        )

    def test_loads_without_error(self, df):
        assert df is not None
        assert len(df) > 0

    def test_row_count_preserved(self, raw_strings, df):
        """No rows silently dropped during coercion."""
        assert len(df) == len(raw_strings), (
            f"Row mismatch: raw={len(raw_strings)}, coerced={len(df)}"
        )

    def test_column_count_preserved(self, raw_strings, df):
        """No columns silently dropped during coercion."""
        assert len(df.columns) == len(raw_strings.columns), (
            f"Column mismatch: raw={len(raw_strings.columns)}, coerced={len(df.columns)}"
        )

    def test_encoding_detected(self, coercion):
        assert coercion.encoding_used in ("utf-8", "latin-1")

    def test_coercion_report_shape_matches(self, df, coercion):
        assert coercion.loaded_rows == len(df)
        assert coercion.loaded_cols == len(df.columns)
        
    def test_coercion_report_has_low_sample_flags(self, coercion):
        assert coercion.suppressed_flags is not None
        assert coercion.low_sample_flags is not None
        assert len(coercion.low_sample_flags) > 0


# ── 2. District/state identifiers detected ────────────────────────────

class TestIdentifierDetection:
    def test_district_col_detected(self, df):
        ids = detect_identifier_columns(df)
        assert len(ids["district_cols"]) >= 1, (
            "Failed to detect any district column"
        )

    def test_state_col_detected(self, df):
        ids = detect_identifier_columns(df)
        assert len(ids["state_cols"]) >= 1, (
            "Failed to detect any state column"
        )

    def test_identifier_columns_are_object_type(self, df):
        ids = detect_identifier_columns(df)
        for col in ids["district_cols"] + ids["state_cols"]:
            assert df[col].dtype == object, (
                f"Identifier column '{col}' should be object type, "
                f"got {df[col].dtype}"
            )


# ── 3. District uniqueness ────────────────────────────────────────────

class TestDistrictUniqueness:
    def test_one_row_per_state_district(self, df):
        ids = detect_identifier_columns(df)
        dcol = ids["district_cols"][0]
        scol = ids["state_cols"][0]
        result = district_uniqueness_audit(df, dcol, scol)
        assert result["one_row_per_combo"], (
            f"Multiple rows per (state, district) combo found. "
            f"Max rows per combo: {result['max_rows_per_combo']}"
        )

    def test_reasonable_district_count(self, df):
        """India has ~730 districts in NFHS-5; sanity check."""
        ids = detect_identifier_columns(df)
        dcol = ids["district_cols"][0]
        scol = ids["state_cols"][0]
        result = district_uniqueness_audit(df, dcol, scol)
        n = result["n_unique_state_district_combos"]
        assert 600 <= n <= 800, (
            f"Expected 600-800 districts, got {n}"
        )


# ── 4. Numeric validation ────────────────────────────────────────────

class TestNumericValidation:
    def test_percentage_columns_within_bounds(self, df):
        """Most percentage columns should have values in [0, 100]."""
        pct_cols = [
            c for c in df.select_dtypes("number").columns
            if "(%" in c.lower() or c.lower().endswith("(%)")
        ]
        for col in pct_cols:
            s = df[col].dropna()
            if len(s) == 0:
                continue
            assert s.min() >= -0.01, (
                f"Column '{col}' has negative values: min={s.min()}"
            )
            assert s.max() <= 100.01, (
                f"Column '{col}' has values > 100: max={s.max()}"
            )

    def test_no_infinite_values(self, df):
        """No column should contain infinite values."""
        for col in df.select_dtypes("number").columns:
            n_inf = int(np.isinf(df[col].dropna()).sum())
            assert n_inf == 0, f"Column '{col}' has {n_inf} infinite values"


# ── 5. Missingness calculations ──────────────────────────────────────

class TestMissingness:
    def test_feature_missingness_sums(self, df):
        fm = feature_missingness(df)
        # Total missing across all columns should be correct
        expected_total = int(df.isna().sum().sum())
        actual_total = int(fm["missing_count"].sum())
        assert actual_total == expected_total

    def test_feature_missingness_percentage_range(self, df):
        fm = feature_missingness(df)
        assert fm["missing_pct"].min() >= 0.0
        assert fm["missing_pct"].max() <= 100.0


# ── 6. Column classification ─────────────────────────────────────────

class TestColumnClassification:
    def test_all_columns_classified(self, df):
        cl = classify_columns(df)
        assert len(cl) == len(df.columns), (
            f"Classification has {len(cl)} entries but dataset has "
            f"{len(df.columns)} columns"
        )

    def test_identifiers_detected(self, df):
        cl = classify_columns(df)
        id_cols = get_columns_by_role(cl, "IDENTIFIER")
        assert len(id_cols) >= 2, (
            f"Expected at least 2 IDENTIFIER columns, got {len(id_cols)}"
        )

    def test_substantive_health_detected(self, df):
        cl = classify_columns(df)
        hi_cols = get_columns_by_role(cl, "SUBSTANTIVE_HEALTH")
        assert len(hi_cols) >= 50, (
            f"Expected at least 50 SUBSTANTIVE_HEALTH columns, got {len(hi_cols)}"
        )
        
    def test_oop_expenditure_classification(self, df):
        cl = classify_columns(df)
        oop_cols = [c for c in cl["column"] if "out-of-pocket expenditure" in c.lower()]
        if oop_cols:
            oop_col = oop_cols[0]
            row = cl[cl["column"] == oop_col].iloc[0]
            assert row["basic_role"] == "HEALTH_SYSTEM"
            assert row["is_health_system"] == True
            assert row["indicator_type"] == "access_affordability"


# ── 7. Audit output generation (integration test) ────────────────────

class TestAuditOutput:
    def test_data_dictionary_can_be_built(self, df, coercion):
        cl = classify_columns(df)
        inv = build_indicator_inventory(df, cl, coercion)
        assert len(inv) == len(df.columns)
        required_cols = ["original_column_name", "clean_name", "domain", "indicator_type", "is_contextual"]
        for rc in required_cols:
            assert rc in inv.columns, f"Missing column '{rc}' in inventory"

    def test_semantic_review_can_be_built(self, df, coercion):
        cl = classify_columns(df)
        inv = build_indicator_inventory(df, cl, coercion)
        sr = generate_semantic_review(df, inv)
        assert len(sr) == len(df.columns)
        assert "is_composite" in sr.columns
        assert "is_derived" in sr.columns

    def test_holdout_registry_can_be_built(self, df, coercion):
        cl = classify_columns(df)
        inv = build_indicator_inventory(df, cl, coercion)
        sr = generate_semantic_review(df, inv)
        hr = generate_holdout_registry(inv, sr)
        assert len(hr) < len(df.columns)  # Identifiers are skipped
        assert "candidate_status" in hr.columns
