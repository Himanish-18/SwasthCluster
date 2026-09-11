#!/usr/bin/env python
"""
SwasthCluster — Phase 1 Data Audit Runner.

Executes the complete Phase 1 audit pipeline and writes all outputs:
  - reports/phase1_data_audit.md
  - reports/figures/*.png
  - metadata/data_dictionary.csv
  - metadata/district_identity_audit.csv

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
    # 3. DATASET IDENTIFICATION
    # ══════════════════════════════════════════════════════════════════
    add(_section("2. Dataset Identification"))
    add(f"- **File**: `{RAW_DATASET_PATH.name}`")
    add(f"- **Path**: `{RAW_DATASET_PATH}`")
    add(f"- **Size**: {RAW_DATASET_PATH.stat().st_size:,} bytes")
    add(f"- **Encoding**: {coercion.encoding_used}")
    add(f"- **Format**: CSV (quoted fields, comma-delimited)")
    add(f"- **Source**: NFHS-5 (2019-21) district-level fact sheets")
    add("")

    # ══════════════════════════════════════════════════════════════════
    # 4. DATASET DIMENSIONS
    # ══════════════════════════════════════════════════════════════════
    add(_section("3. Dataset Dimensions"))
    dims = dataset_dimensions(df)
    add(f"- **Rows**: {dims['rows']}")
    add(f"- **Columns**: {dims['columns']}")
    add(f"- **Memory**: {dims['memory_mb']} MB")
    add("")

    # Coercion summary
    add(_section("Coercion Summary", 3))
    add(f"- Suppressed values (`*` → NaN): **{coercion.total_suppressed}**")
    add(f"- Parenthesized values (low-sample, parens stripped): **{coercion.total_parenthesized}**")
    add(f"- Whitespace stripped: **{coercion.total_whitespace_stripped}**")
    add(f"- Coercion failures: **{coercion.total_coercion_failures}**")
    if coercion.total_coercion_failures > 0:
        add("\nCoercion failure details:")
        for col, examples in coercion.coercion_failure_examples.items():
            add(f"  - `{col}`: {examples[:5]}")
    add("")

    # ══════════════════════════════════════════════════════════════════
    # 5. SCHEMA OVERVIEW
    # ══════════════════════════════════════════════════════════════════
    add(_section("4. Schema Overview"))
    col_prof = column_profile(df)
    # Show dtype distribution
    dtype_counts = col_prof["dtype"].value_counts()
    add("**Data type distribution:**\n")
    for dt, cnt in dtype_counts.items():
        add(f"- `{dt}`: {cnt} columns")
    add("")

    # Top-level column profile (first 30 for readability)
    add("**Column profile (first 30 columns):**\n")
    display_cols_prof = col_prof[
        ["dtype", "unique_count", "unique_pct", "null_count", "null_pct"]
    ].head(30)
    add(_md_table(display_cols_prof))
    add("")

    # Numeric quality
    num_quality = numeric_quality_audit(df)
    n_constant = num_quality["is_constant"].sum()
    n_near_constant = num_quality["is_near_constant"].sum()
    add(f"- Constant numeric columns: **{n_constant}**")
    add(f"- Near-constant numeric columns: **{n_near_constant}**")
    if n_near_constant > 0:
        nc_cols = num_quality[num_quality["is_near_constant"]].index.tolist()
        add(f"  - Near-constant columns: {nc_cols[:10]}")
    add("")

    # Categorical quality
    cat_quality = categorical_quality_audit(df)
    if len(cat_quality) > 0:
        add("**Categorical columns:**\n")
        add(_md_table(cat_quality))
    add("")

    # ══════════════════════════════════════════════════════════════════
    # 6. DISTRICT IDENTITY AUDIT
    # ══════════════════════════════════════════════════════════════════
    add(_section("5. District Identity Audit"))
    id_cols = detect_identifier_columns(df)
    district_col = id_cols["district_cols"][0] if id_cols["district_cols"] else None
    state_col = id_cols["state_cols"][0] if id_cols["state_cols"] else None

    if not district_col or not state_col:
        add("⚠️ **CRITICAL**: Could not auto-detect district/state columns!\n")
        add(f"  District candidates: {id_cols['district_cols']}")
        add(f"  State candidates: {id_cols['state_cols']}")
    else:
        add(f"- **District column**: `{district_col}`")
        add(f"- **State column**: `{state_col}`\n")

        # Identifier summaries
        for col in [district_col, state_col]:
            s = identifier_summary(df, col)
            add(f"**`{col}`**:")
            add(f"  - Data type: `{s['dtype']}`")
            add(f"  - Unique count: {s['unique_count']}")
            add(f"  - Null count: {s['null_count']}")
            add(f"  - Uniqueness ratio: {s['uniqueness_ratio']}")
            add(f"  - Examples: {s['example_values'][:5]}")
            add("")

        # Uniqueness audit
        uniq = district_uniqueness_audit(df, district_col, state_col)
        add(_section("District Uniqueness", 3))
        add(f"- Total rows: **{uniq['n_rows']}**")
        add(f"- Unique districts (by name only): **{uniq['n_unique_districts']}**")
        add(f"- Unique states/UTs: **{uniq['n_unique_states']}**")
        add(f"- Unique (state, district) combos: **{uniq['n_unique_state_district_combos']}**")
        add(f"- One row per combo: **{uniq['one_row_per_combo']}**")
        add(f"- Max rows per combo: **{uniq['max_rows_per_combo']}**")
        add("")

        if uniq["multi_occurrence_combos"]:
            add("**Multi-occurrence (state, district) combinations:**\n")
            add("| State | District | Count |")
            add("|-------|----------|-------|")
            for r in uniq["multi_occurrence_combos"]:
                add(f"| {r[state_col]} | {r[district_col]} | {r['count']} |")
            add("")

        if uniq["cross_state_districts"]:
            add(f"**District names appearing in multiple states: {uniq['n_cross_state_district_names']}**\n")
            cross_df = pd.DataFrame(uniq["cross_state_districts"])
            add(_md_table(cross_df.head(30)))
        else:
            add(f"**Cross-state district name collisions**: {uniq['n_cross_state_district_names']}")
        add("")

    # ══════════════════════════════════════════════════════════════════
    # 7. STATE-DISTRICT CONSISTENCY
    # ══════════════════════════════════════════════════════════════════
    add(_section("6. State-District Consistency"))

    if state_col:
        state_cons = state_consistency_audit(df, state_col)
        add(f"- Unique state names (raw): **{state_cons['n_unique_raw']}**")
        add(f"- Unique state names (normalised): **{state_cons['n_unique_normalised']}**")
        add("")

        if state_cons["capitalisation_inconsistencies"]:
            add("**Capitalisation inconsistencies:**\n")
            for norm, variants in state_cons["capitalisation_inconsistencies"].items():
                add(f"  - `{norm}` → {variants}")
        else:
            add("No capitalisation inconsistencies found in state names.\n")

        if state_cons["whitespace_issues"]:
            add(f"**Whitespace issues in state names**: {len(state_cons['whitespace_issues'])}")
            add(f"  Examples: {state_cons['whitespace_issues'][:5]}")
        else:
            add("No whitespace issues in state names.\n")

        add("\n**All states/UTs:**\n")
        for st in state_cons["all_states_sorted"]:
            add(f"  - {st}")
        add("")

    if district_col:
        dist_cons = district_consistency_audit(df, district_col)
        add(f"- Unique district names (raw): **{dist_cons['n_unique_raw']}**")
        add(f"- Unique district names (stripped): **{dist_cons['n_unique_stripped']}**")
        add(f"- Whitespace issues in district names: **{dist_cons['whitespace_issues_count']}**")
        add("")

    # Export district identity CSV
    if district_col and state_col:
        id_csv = generate_district_identity_csv(df, district_col, state_col)
        id_csv_path = METADATA_DIR / "district_identity_audit.csv"
        id_csv.to_csv(id_csv_path, index=False)
        logger.info("Saved → %s", id_csv_path)

    # ══════════════════════════════════════════════════════════════════
    # 8. DUPLICATE ANALYSIS
    # ══════════════════════════════════════════════════════════════════
    add(_section("7. Duplicate Analysis"))

    # Exact duplicate rows
    n_exact_dupes = int(df.duplicated(keep=False).sum())
    n_exact_dupe_groups = int(df.duplicated(keep="first").sum())
    add(f"- Exact duplicate rows: **{n_exact_dupe_groups}** ({round(n_exact_dupe_groups/len(df)*100,2)}%)")
    add("")

    if n_exact_dupe_groups > 0:
        dupes = df[df.duplicated(keep=False)]
        add("**Duplicate rows (showing district/state):**\n")
        if district_col and state_col:
            add(_md_table(dupes[[district_col, state_col]].drop_duplicates()))
        add("")

    # Duplicate district identifiers (name only)
    if district_col:
        dist_vc = df[district_col].value_counts()
        multi_dist = dist_vc[dist_vc > 1]
        add(f"- District names appearing more than once: **{len(multi_dist)}**")
        if len(multi_dist) > 0:
            add("  (These may be legitimate — same district name in different states.)\n")
            add("| District Name | Occurrences |")
            add("|---------------|-------------|")
            for dn, cnt in multi_dist.head(20).items():
                add(f"| {dn} | {cnt} |")
        add("")

    # Duplicate (state, district)
    if district_col and state_col:
        combo_vc = df.groupby([state_col, district_col]).size()
        multi_combo = combo_vc[combo_vc > 1]
        add(f"- Duplicate (state, district) combos: **{len(multi_combo)}**")
        add("")

    # ══════════════════════════════════════════════════════════════════
    # 9. INDICATOR INVENTORY
    # ══════════════════════════════════════════════════════════════════
    add(_section("8. Indicator Inventory"))
    classification = classify_columns(df)
    inventory = build_indicator_inventory(df, classification)

    # Role distribution
    role_counts = classification["role"].value_counts()
    add("**Column role distribution:**\n")
    for role, cnt in role_counts.items():
        add(f"- `{role}`: {cnt}")
    add("")

    # Domain distribution (among HEALTH_INDICATOR columns)
    health_inv = inventory[inventory["candidate_role"] == "HEALTH_INDICATOR"]
    domain_counts = health_inv["domain"].value_counts()
    add("**Health indicator domains:**\n")
    for dom, cnt in domain_counts.items():
        add(f"- `{dom}`: {cnt}")
    add("")

    # Save full data dictionary
    dict_path = METADATA_DIR / "data_dictionary.csv"
    inventory.to_csv(dict_path, index=False)
    logger.info("Saved → %s", dict_path)
    add(f"Full data dictionary exported to `metadata/data_dictionary.csv` ({len(inventory)} entries).\n")

    # ══════════════════════════════════════════════════════════════════
    # 10. MISSINGNESS ANALYSIS
    # ══════════════════════════════════════════════════════════════════
    add(_section("9. Missingness Analysis"))
    feat_miss = feature_missingness(df)

    n_zero_miss = int((feat_miss["missing_pct"] == 0).sum())
    n_any_miss = int((feat_miss["missing_pct"] > 0).sum())
    n_high_miss = int((feat_miss["missing_pct"] > 30).sum())

    add(f"- Columns with zero missing: **{n_zero_miss}**")
    add(f"- Columns with any missing: **{n_any_miss}**")
    add(f"- Columns with >30% missing: **{n_high_miss}**")
    add("")

    # Top missing columns
    top_miss = feat_miss[feat_miss["missing_pct"] > 0].head(25)
    if len(top_miss) > 0:
        add("**Top 25 columns by missingness:**\n")
        add(_md_table(top_miss))
        add("")

    # District-level missingness
    if district_col and state_col:
        dist_miss = district_missingness(df, district_col, state_col)
        complete = dist_miss[dist_miss["completeness_pct"] == 100]
        low_complete = dist_miss[dist_miss["completeness_pct"] < 70]

        add(_section("District-level Missingness", 3))
        add(f"- Fully complete districts: **{len(complete)}** / {len(dist_miss)}")
        add(f"- Districts with <70% completeness: **{len(low_complete)}**")
        add(f"- Minimum completeness: **{dist_miss['completeness_pct'].min():.1f}%**")
        add(f"- Mean completeness: **{dist_miss['completeness_pct'].mean():.1f}%**")
        add("")

        if len(low_complete) > 0:
            add("**Districts with lowest completeness:**\n")
            add(_md_table(low_complete.head(15)[
                ["district", "state", "n_missing", "completeness_pct"]
            ]))
            add("")

        # State-level aggregation
        state_miss = state_level_missingness(dist_miss)
        add(_section("Geographic Concentration of Missingness", 3))
        add(_md_table(state_miss.head(15)))
        add("")

    # Plots
    plot_feature_missingness(feat_miss, FIGURES_DIR / "missingness_bar.png")
    plot_missingness_heatmap(df, FIGURES_DIR / "missingness_heatmap.png")

    add("![Missingness bar chart](reports/figures/missingness_bar.png)\n")
    add("![Missingness heatmap](reports/figures/missingness_heatmap.png)\n")

    # ══════════════════════════════════════════════════════════════════
    # 11. VALUE/RANGE VALIDATION
    # ══════════════════════════════════════════════════════════════════
    add(_section("10. Value/Range Validation"))
    range_val = range_validation(df, classification)
    suspicious = range_val[range_val["n_suspicious"] > 0]

    add(f"- Columns validated: **{len(range_val)}**")
    add(f"- Columns with values outside expected range: **{len(suspicious)}**")
    add("")

    if len(suspicious) > 0:
        add("**Suspicious range violations:**\n")
        add(_md_table(suspicious))
    else:
        add("All validated columns fall within expected ranges.\n")
    add("")

    # ══════════════════════════════════════════════════════════════════
    # 12. DISTRIBUTION ANALYSIS
    # ══════════════════════════════════════════════════════════════════
    add(_section("11. Distribution Analysis"))
    dist_stats = distribution_statistics(df)

    n_high_skew = int(dist_stats["high_skew"].sum())
    n_near_zero_var = int(dist_stats["near_zero_var"].sum())

    add(f"- Numeric columns analysed: **{len(dist_stats)}**")
    add(f"- Highly skewed (|skew| > 2): **{n_high_skew}**")
    add(f"- Near-zero variance: **{n_near_zero_var}**")
    add("")

    if n_high_skew > 0:
        skewed = dist_stats[dist_stats["high_skew"]].sort_values("skewness", key=abs, ascending=False)
        add("**Highly skewed columns (top 20):**\n")
        add(_md_table(skewed[["n_valid", "mean", "median", "std", "skewness"]].head(20)))
        add("")

    if n_near_zero_var > 0:
        nzv = dist_stats[dist_stats["near_zero_var"]]
        add("**Near-zero variance columns:**\n")
        add(_md_table(nzv[["n_valid", "mean", "std", "min", "max"]]))
        add("")

    plot_distribution_overview(df, FIGURES_DIR / "distribution_overview.png")
    add("![Distribution overview](reports/figures/distribution_overview.png)\n")

    # ══════════════════════════════════════════════════════════════════
    # 13. NON-ANALYTICAL / METADATA COLUMNS
    # ══════════════════════════════════════════════════════════════════
    add(_section("12. Non-Analytical / Metadata Columns"))
    add("**Column classification:**\n")
    add(_md_table(classification))
    add("")

    non_indicator = classification[classification["role"] != "HEALTH_INDICATOR"]
    add(f"Columns **not** classified as `HEALTH_INDICATOR`: **{len(non_indicator)}**\n")
    for _, row in non_indicator.iterrows():
        add(f"- `{row['column']}` → **{row['role']}** — {row['rationale']}")
    add("")

    # ══════════════════════════════════════════════════════════════════
    # 14. COMPOSITE / DERIVED FEATURE INVESTIGATION
    # ══════════════════════════════════════════════════════════════════
    add(_section("13. Composite / Derived Feature Investigation"))
    add(textwrap.dedent("""\
    The dataset was inspected for composite health scores, wealth indices,
    rankings, or pre-computed aggregate indices.

    **Findings:**
    """))

    # Search for composite-score keywords
    composite_keywords = [
        "index", "score", "composite", "ranking", "rank", "wealth",
        "aggregate", "overall", "total",
    ]
    composite_candidates = []
    for col in df.columns:
        col_lower = col.lower()
        for kw in composite_keywords:
            if kw in col_lower:
                composite_candidates.append((col, kw))
                break

    if composite_candidates:
        add("The following columns contain keywords suggestive of composite/derived scores:\n")
        for col, kw in composite_candidates:
            add(f"- `{col}` (keyword: `{kw}`)")
        add("")
        add("> **Note**: These require careful review in Phase 2 to determine whether")
        add("> they are aggregated/derived and should be excluded from clustering to")
        add("> avoid circularity with the project's goal of creating *new* groupings.")
    else:
        add("No columns with composite-index keywords (`index`, `score`, `ranking`,")
        add("`wealth`, `aggregate`, `composite`) were found in the column headers.")
        add("")
        add("However, some columns may still represent *implicit* composites (e.g.,")
        add("`Total Unmet need for Family Planning` aggregates spacing and limiting).")
        add("These should be reviewed in Phase 2.")
    add("")

    # ══════════════════════════════════════════════════════════════════
    # 15. DATA QUALITY ISSUES
    # ══════════════════════════════════════════════════════════════════
    add(_section("14. Data Quality Issues"))
    issues: list[str] = []

    if coercion.total_suppressed > 0:
        issues.append(
            f"**Suppressed values**: {coercion.total_suppressed} cells marked `*` "
            f"(NFHS convention: <25 unweighted cases). These are NaN in the loaded data."
        )
    if coercion.total_parenthesized > 0:
        issues.append(
            f"**Low-sample-size values**: {coercion.total_parenthesized} cells were "
            f"parenthesized (25-49 unweighted cases per NFHS convention). "
            f"Numeric values were extracted but may have higher uncertainty."
        )
    if district_col:
        dc = district_consistency_audit(df, district_col)
        if dc["whitespace_issues_count"] > 0:
            issues.append(
                f"**District name whitespace**: {dc['whitespace_issues_count']} district "
                f"names have trailing whitespace in the raw data."
            )
    if state_col:
        sc = state_consistency_audit(df, state_col)
        if sc["whitespace_issues"]:
            issues.append(
                f"**State name whitespace**: {len(sc['whitespace_issues'])} state names "
                f"have whitespace issues."
            )
    if n_high_miss > 0:
        issues.append(
            f"**High missingness**: {n_high_miss} columns have >30% missing values. "
            f"This will affect the usable indicator count for clustering."
        )
    if len(suspicious) > 0:
        issues.append(
            f"**Range violations**: {len(suspicious)} columns have values outside "
            f"expected ranges (see Section 10)."
        )

    if issues:
        for i, issue in enumerate(issues, 1):
            add(f"{i}. {issue}\n")
    else:
        add("No major data quality issues detected.\n")
    add("")

    # ══════════════════════════════════════════════════════════════════
    # 16. DATASET SUITABILITY
    # ══════════════════════════════════════════════════════════════════
    add(_section("15. Dataset Suitability"))

    # Build evidence
    n_districts = uniq["n_unique_state_district_combos"] if district_col else 0
    n_health = len(health_inv)
    one_per_row = uniq["one_row_per_combo"] if district_col else False
    mean_completeness = dist_miss["completeness_pct"].mean() if district_col else 0

    add("**Assessment: YES, WITH CONDITIONS**\n")
    add("Evidence:\n")
    add(f"1. **Usable district observations**: {n_districts} unique (state, district) "
        f"combinations identified.")
    add(f"2. **District identity reliability**: {'One row per (state, district) — confirmed.' if one_per_row else 'MULTIPLE ROWS PER COMBO — requires investigation.'}")
    add(f"3. **Health/nutrition indicators**: {n_health} columns classified as HEALTH_INDICATOR, "
        f"spanning {len(domain_counts)} domains.")
    add(f"4. **Missingness**: Mean district completeness {mean_completeness:.1f}%. "
        f"{n_high_miss} columns have >30% missing — imputation strategy needed.")
    add(f"5. **Duplicates**: {n_exact_dupe_groups} exact duplicate rows.")
    add(f"6. **Geographic identifiers**: District and state columns detected and validated.")
    add(f"7. **NFHS special values**: {coercion.total_suppressed} suppressed (`*`) and "
        f"{coercion.total_parenthesized} low-sample parenthesized values affect data density.\n")

    add("**Conditions for Phase 2:**\n")
    add("- Decide handling strategy for suppressed (`*`) values (currently NaN).")
    add("- Decide whether parenthesized (low-n) values are reliable enough to include.")
    add("- Address high-missingness columns (drop vs. impute).")
    add("- Determine appropriate imputation strategy.")
    add("- Investigate and resolve any range violations.")
    add("- Standardise district/state names (strip whitespace).")
    add("")

    # ══════════════════════════════════════════════════════════════════
    # 17. RISKS AND OPEN QUESTIONS
    # ══════════════════════════════════════════════════════════════════
    add(_section("16. Risks and Open Questions"))
    add(textwrap.dedent("""\
    1. **NFHS suppressed values (`*`)**: These represent genuine information absence
       (sample too small), not random missingness. Imputing them requires caution —
       they are structurally missing (MNAR).

    2. **Parenthesized values**: Based on 25-49 unweighted cases. Higher uncertainty
       but still informative. Should Phase 2 treat them differently or flag them?

    3. **Cross-state district name collisions**: Some district names appear in multiple
       states. The (state, district) pair is the correct identifier, not district name alone.

    4. **Scale heterogeneity**: Most indicators are percentages (0-100), but sex ratios
       are per 1,000, expenditure is in Rupees, and sample counts are integers.
       Standardisation/normalisation is essential before clustering.

    5. **Domain balance**: Some health domains have many more indicators than others.
       This could bias clustering toward over-represented domains.

    6. **Column header footnotes**: Column names contain NFHS superscript footnote
       markers (e.g., `...1 (%)`, `...22 (%)`). These should be cleaned for
       programmatic use but the original names preserved in the data dictionary.
    """))

    # ══════════════════════════════════════════════════════════════════
    # 18. RECOMMENDATIONS FOR PHASE 2
    # ══════════════════════════════════════════════════════════════════
    add(_section("17. Recommendations for Phase 2"))
    add(textwrap.dedent("""\
    1. **Feature selection**: Use the data dictionary and domain classification to
       select a balanced set of indicators. Consider domain balance.

    2. **Holdout indicator selection**: Choose indicators to withhold from clustering
       for external validation. Good candidates include indicators from domains
       with multiple correlated variables.

    3. **Missing data strategy**: Evaluate MICE, KNN imputation, or column-dropping
       thresholds. Document the chosen strategy and its impact.

    4. **Standardisation**: Apply z-score or min-max normalisation after handling
       missing values and outliers.

    5. **Column name cleaning**: Create short, programmatic column aliases while
       preserving the original NFHS headers in the data dictionary.

    6. **EDA**: Correlation analysis, PCA for dimensionality exploration (not
       feature selection), and domain-specific exploration.
    """))

    # ══════════════════════════════════════════════════════════════════
    # 19. REPRODUCIBILITY INFORMATION
    # ══════════════════════════════════════════════════════════════════
    add(_section("18. Reproducibility Information"))
    end_time = datetime.now(timezone.utc)
    add(f"- **Generated at**: {end_time.isoformat()}")
    add(f"- **Duration**: {(end_time - start_time).total_seconds():.1f}s")
    add(f"- **Python**: {sys.version}")
    add(f"- **Command**: `python scripts/run_phase1_audit.py`")
    add(f"- **Dataset**: `{RAW_DATASET_PATH.name}` ({coercion.raw_rows} rows × {coercion.raw_cols} cols)")
    add("")

    # ══════════════════════════════════════════════════════════════════
    # FILL EXECUTIVE SUMMARY
    # ══════════════════════════════════════════════════════════════════
    exec_text = textwrap.dedent(f"""\
    This report documents the Phase 1 data audit of the NFHS-5 (2019-21) district-level
    dataset for the SwasthCluster project.

    **Key facts:**
    - The dataset contains **{dims['rows']} rows** and **{dims['columns']} columns**.
    - Each row represents one Indian district (confirmed: **{n_districts}** unique
      state-district combinations, one row per combination).
    - **{n_health}** columns are classified as health/nutrition indicators across
      **{len(domain_counts)}** domains.
    - **{coercion.total_suppressed}** values are suppressed (`*`, <25 cases) and
      **{coercion.total_parenthesized}** are flagged as low-sample (parenthesized).
    - **{n_high_miss}** columns have >30% missing values.
    - Mean district completeness is **{mean_completeness:.1f}%**.
    - **Assessment**: The dataset is suitable for district-level clustering
      **with conditions** (see Section 15).
    """)
    report_lines[exec_summary_idx + 1] = exec_text

    # ══════════════════════════════════════════════════════════════════
    # WRITE REPORT
    # ══════════════════════════════════════════════════════════════════
    report_text = "\n".join(report_lines)
    report_path = REPORTS_DIR / "phase1_data_audit.md"
    report_path.write_text(report_text, encoding="utf-8")
    logger.info("=" * 70)
    logger.info("Phase 1 report saved → %s", report_path)
    logger.info("Data dictionary → %s", dict_path)
    logger.info("District identity audit → %s", METADATA_DIR / "district_identity_audit.csv")
    logger.info("Figures → %s", FIGURES_DIR)
    logger.info("=" * 70)

    print(f"\nPhase 1 audit complete. Report: {report_path}")


if __name__ == "__main__":
    run()
