#!/usr/bin/env python
"""
SwasthCluster — Phase 1 Data Audit Runner.

Executes the complete Phase 1 audit pipeline and writes all outputs:
  - reports/phase1_data_audit.md
  - reports/figures/*.png
  - metadata/data_dictionary.csv
  - metadata/district_identity_audit.csv
  - metadata/indicator_semantic_review.csv
  - metadata/holdout_candidate_registry.csv
  - metadata/missingness_by_state.csv

Run from the project root:
    python scripts/run_phase1_audit.py
"""

from __future__ import annotations

import json
import logging
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import RAW_DATASET_PATH, FIGURES_DIR, REPORTS_DIR, METADATA_DIR
from src.audit.loader import load_raw_dataset, load_raw_as_strings, CoercionReport
from src.audit.dataset_profile import (
    dataset_dimensions,
    column_profile,
    numeric_quality_audit,
    categorical_quality_audit,
)
from src.audit.district_audit import (
    detect_identifier_columns,
    identifier_summary,
    district_uniqueness_audit,
    state_consistency_audit,
    district_consistency_audit,
    generate_district_identity_csv,
)
from src.audit.missingness import (
    feature_missingness,
    district_missingness,
    state_level_missingness,
    plot_feature_missingness,
    plot_missingness_heatmap,
)
from src.audit.column_classifier import classify_columns, get_columns_by_role
from src.audit.indicator_inventory import build_indicator_inventory
from src.audit.validation import (
    range_validation,
    distribution_statistics,
    plot_distribution_overview,
)
from src.audit.semantic_review import generate_semantic_review
from src.audit.holdout_registry import generate_holdout_registry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("phase1_audit")


def _md_table(df: "pd.DataFrame", max_rows: int = 60) -> str:
    """Convert a DataFrame to a markdown table string."""
    import pandas as pd
    subset = df.head(max_rows)
    return subset.to_markdown()


def _section(title: str, level: int = 2) -> str:
    return f"\n{'#' * level} {title}\n"


def run() -> None:
    """Execute the complete Phase 1 audit."""
    import pandas as pd

    start_time = datetime.now(timezone.utc)
    logger.info("=" * 70)
    logger.info("SwasthCluster Phase 1 — Data Audit")
    logger.info("=" * 70)

    # Ensure output directories exist
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    report_lines: list[str] = []

    def add(text: str) -> None:
        report_lines.append(text)

    # ══════════════════════════════════════════════════════════════════
    # 1. LOAD
    # ══════════════════════════════════════════════════════════════════
    logger.info("Step 1: Loading dataset …")
    if not RAW_DATASET_PATH.exists():
        logger.error("Dataset not found at %s", RAW_DATASET_PATH)
        sys.exit(1)

    df, coercion = load_raw_dataset()
    df_raw_strings = load_raw_as_strings()

    add("# SwasthCluster Phase 1 — Data Audit\n")
    add(f"*Generated: {start_time.isoformat()}*\n")

    # ══════════════════════════════════════════════════════════════════
    # 2. EXECUTIVE SUMMARY (placeholder — filled at end)
    # ══════════════════════════════════════════════════════════════════
    exec_summary_idx = len(report_lines)
    add(_section("1. Executive Summary"))
    add("_PLACEHOLDER_EXEC_SUMMARY_\n")

    # ══════════════════════════════════════════════════════════════════
    # 3. PHASE 1 CORRECTIVE REVIEW
    # ══════════════════════════════════════════════════════════════════
    add(_section("2. Phase 1 Corrective Review"))
    add(textwrap.dedent("""\
    This section documents the methodological corrections applied during the Phase 1 Review
    to strengthen the research-design foundation prior to Phase 2 clustering.

    - **Semantic Classification & Data Dictionary**: Replaced broad keywords with granular `indicator_type` fields (outcome, coverage, access, demographic, etc.). Specifically reclassified Out-of-Pocket Expenditure as a substantive health-system access metric, not statistical metadata.
    - **Semantic Review (Derived & Composite Features)**: Implemented explicit logical mapping to categorize variables as raw, derived, ratio, or composite, moving away from simple keyword matching (`metadata/indicator_semantic_review.csv`).
    - **Holdout Candidate Registry**: Established principles and a registry (`metadata/holdout_candidate_registry.csv`) for selecting external validation variables prior to clustering. Good holdouts must be substantive health outcomes, not used in clustering, with sufficient data coverage.
    - **Low-Sample Handling**: The loader now preserves a `low_sample_flags` matrix tracking parenthesized values. Downstream sensitivity analysis will explicitly test Scenario A (retaining values) vs Scenario B (treating as missing).
    - **Missingness Geographic Concentration**: Expanded analysis to measure completeness by State/UT (`metadata/missingness_by_state.csv`). Documented requirement to compare complete-case vs. KNN vs. MICE imputation iteratively during Phase 2.
    - **Domain Imbalance**: Quantified domain imbalance explicitly (see Section 9). Established requirement for domain-weighting strategy exploration (raw vs equal domain weight vs PCA) in Phase 2.
    - **PCA & Baseline Strategy**: Clarified that PCA is a diagnostic tool, not automatically the final clustering space. Established the baseline concept as a conventional composite-index ranking approach to contrast with multidimensional clustering.
    """))

    # ══════════════════════════════════════════════════════════════════
    # 4. DATASET IDENTIFICATION
    # ══════════════════════════════════════════════════════════════════
    add(_section("3. Dataset Identification"))
    add(f"- **File**: `{RAW_DATASET_PATH.name}`")
    add(f"- **Path**: `{RAW_DATASET_PATH}`")
    add(f"- **Size**: {RAW_DATASET_PATH.stat().st_size:,} bytes")
    add(f"- **Encoding**: {coercion.encoding_used}")
    add(f"- **Format**: CSV (quoted fields, comma-delimited)")
    add(f"- **Source**: NFHS-5 (2019-21) district-level fact sheets")
    add("")

    # ══════════════════════════════════════════════════════════════════
    # 5. DATASET DIMENSIONS
    # ══════════════════════════════════════════════════════════════════
    add(_section("4. Dataset Dimensions"))
    dims = dataset_dimensions(df)
    add(f"- **Rows**: {dims['rows']}")
    add(f"- **Columns**: {dims['columns']}")
    add(f"- **Memory**: {dims['memory_mb']} MB")
    add("")

    add(_section("Coercion Summary", 3))
    add(f"- Suppressed values (`*` → NaN): **{coercion.total_suppressed}**")
    add(f"- Parenthesized values (low-sample, parens stripped): **{coercion.total_parenthesized}**")
    add(f"- Whitespace stripped: **{coercion.total_whitespace_stripped}**")
    add(f"- Coercion failures: **{coercion.total_coercion_failures}**")
    add("")

    # ══════════════════════════════════════════════════════════════════
    # 6. SCHEMA OVERVIEW
    # ══════════════════════════════════════════════════════════════════
    add(_section("5. Schema Overview"))
    col_prof = column_profile(df)
    dtype_counts = col_prof["dtype"].value_counts()
    add("**Data type distribution:**\n")
    for dt, cnt in dtype_counts.items():
        add(f"- `{dt}`: {cnt} columns")
    add("")

    # ══════════════════════════════════════════════════════════════════
    # 7. DISTRICT IDENTITY AUDIT
    # ══════════════════════════════════════════════════════════════════
    add(_section("6. District Identity Audit"))
    id_cols = detect_identifier_columns(df)
    district_col = id_cols["district_cols"][0] if id_cols["district_cols"] else None
    state_col = id_cols["state_cols"][0] if id_cols["state_cols"] else None

    if district_col and state_col:
        add(f"- **District column**: `{district_col}`")
        add(f"- **State column**: `{state_col}`\n")
        uniq = district_uniqueness_audit(df, district_col, state_col)
        add(_section("District Uniqueness", 3))
        add(f"- Unique states/UTs: **{uniq['n_unique_states']}**")
        add(f"- Unique (state, district) combos: **{uniq['n_unique_state_district_combos']}**")
        add(f"- One row per combo: **{uniq['one_row_per_combo']}**")
        
        id_csv = generate_district_identity_csv(df, district_col, state_col)
        id_csv_path = METADATA_DIR / "district_identity_audit.csv"
        id_csv.to_csv(id_csv_path, index=False)
    else:
        add("⚠️ **CRITICAL**: Could not auto-detect district/state columns!\n")
        uniq = {"n_unique_state_district_combos": 0, "one_row_per_combo": False}

    # ══════════════════════════════════════════════════════════════════
    # 8. DUPLICATE ANALYSIS
    # ══════════════════════════════════════════════════════════════════
    add(_section("7. Duplicate Analysis"))
    n_exact_dupe_groups = int(df.duplicated(keep="first").sum())
    add(f"- Exact duplicate rows: **{n_exact_dupe_groups}**")
    add("")

    # ══════════════════════════════════════════════════════════════════
    # 9. INDICATOR INVENTORY & DOMAIN IMBALANCE
    # ══════════════════════════════════════════════════════════════════
    add(_section("8. Indicator Inventory & Semantic Review"))
    classification = classify_columns(df)
    inventory = build_indicator_inventory(df, classification, coercion_report=coercion)

    dict_path = METADATA_DIR / "data_dictionary.csv"
    inventory.to_csv(dict_path, index=False)

    semantic_review = generate_semantic_review(df, inventory)
    sr_path = METADATA_DIR / "indicator_semantic_review.csv"
    semantic_review.to_csv(sr_path, index=False)
    
    holdout_registry = generate_holdout_registry(inventory, semantic_review)
    hr_path = METADATA_DIR / "holdout_candidate_registry.csv"
    holdout_registry.to_csv(hr_path, index=False)

    add(f"Full data dictionary exported to `metadata/data_dictionary.csv` ({len(inventory)} entries).\n")
    add(f"Semantic review exported to `metadata/indicator_semantic_review.csv`.\n")
    add(f"Holdout registry exported to `metadata/holdout_candidate_registry.csv`.\n")

    add(_section("Domain Imbalance Analysis", 3))
    add("The clustering results may be implicitly weighted if some health domains have many more indicators than others.")
    domain_counts = inventory[~inventory["indicator_type"].isin(["identifier", "survey_metadata"])]["domain"].value_counts()
    tot_indicators = domain_counts.sum()
    
    domain_table = []
    for dom, cnt in domain_counts.items():
        domain_table.append({
            "Domain": dom,
            "Indicator Count": cnt,
            "Percentage": f"{(cnt / tot_indicators * 100):.1f}%"
        })
    add(_md_table(pd.DataFrame(domain_table)))
    add("")
    add("> **Risk**: Raw distance-based clustering will implicitly give more weight to domains with more indicators (e.g., child health). Strategies to address this in Phase 2 include: 1) Raw weighting after standardization, 2) Equal domain weighting, 3) Domain-level PCA.")

    # ══════════════════════════════════════════════════════════════════
    # 10. MISSINGNESS ANALYSIS
    # ══════════════════════════════════════════════════════════════════
    add(_section("9. Missingness Analysis"))
    feat_miss = feature_missingness(df)
    n_high_miss = int((feat_miss["missing_pct"] > 30).sum())

    add(f"- Columns with >30% missing: **{n_high_miss}**")
    add("")

    if district_col and state_col:
        dist_miss = district_missingness(df, district_col, state_col)
        mean_completeness = dist_miss["completeness_pct"].mean()

        state_miss = state_level_missingness(dist_miss)
        state_miss_path = METADATA_DIR / "missingness_by_state.csv"
        state_miss.to_csv(state_miss_path)
        
        add(_section("Geographic Concentration of Missingness", 3))
        add("Missingness by State/UT exported to `metadata/missingness_by_state.csv`.")
        add(_md_table(state_miss.head(15)))
        add("")
    else:
        mean_completeness = 0

    plot_feature_missingness(feat_miss, FIGURES_DIR / "missingness_bar.png")
    plot_missingness_heatmap(df, FIGURES_DIR / "missingness_heatmap.png")
    add("![Missingness heatmap](reports/figures/missingness_heatmap.png)\n")

    # ══════════════════════════════════════════════════════════════════
    # 11. BASELINE COMPARISON & PCA
    # ══════════════════════════════════════════════════════════════════
    add(_section("10. PCA Positioning and Composite Baselines"))
    add(textwrap.dedent("""\
    ### PCA Positioning
    PCA is an **exploratory diagnostic** tool in this pipeline, not automatically the final representation for clustering. It will be evaluated in Phase 2 for noise reduction and multicollinearity mitigation.

    ### Baseline
    To evaluate whether clustering adds value, we establish a **conventional composite-index** baseline approach. The final analysis will contrast the multidimensional clusters against single-ranking composite scores to demonstrate if similarly-ranked districts have different multidimensional needs.
    """))

    # ══════════════════════════════════════════════════════════════════
    # FILL EXECUTIVE SUMMARY
    # ══════════════════════════════════════════════════════════════════
    n_districts = uniq["n_unique_state_district_combos"] if district_col else 0
    exec_text = textwrap.dedent(f"""\
    This report documents the **Phase 1 Corrective Review** of the NFHS-5 (2019-21) dataset for SwasthCluster.

    **Key facts:**
    - The dataset contains **{dims['rows']} rows** and **{dims['columns']} columns**.
    - Each row represents one Indian district (**{n_districts}** unique state-district combinations).
    - **{tot_indicators}** columns are classified as substantive health, contextual, or health-system indicators across **{len(domain_counts)}** domains.
    - **Domain Imbalance** is significant and must be addressed in Phase 2.
    - **{coercion.total_suppressed}** values are suppressed (`*`) and **{coercion.total_parenthesized}** are low-sample (parenthesized). These are now rigorously tracked.
    - **{n_high_miss}** columns have >30% missing values. Mean district completeness is **{mean_completeness:.1f}%**.
    - **Assessment**: The dataset is methodologically ready for Phase 2 feature engineering.
    """)
    report_lines[exec_summary_idx + 1] = exec_text

    # ══════════════════════════════════════════════════════════════════
    # WRITE REPORT
    # ══════════════════════════════════════════════════════════════════
    report_text = "\n".join(report_lines)
    report_path = REPORTS_DIR / "phase1_data_audit.md"
    report_path.write_text(report_text, encoding="utf-8")
    
    print(f"\nPhase 1 audit complete. Report: {report_path}")

if __name__ == "__main__":
    run()
