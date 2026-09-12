# SwasthCluster Phase 1 — Data Audit

*Generated: 2026-09-12T17:29:52.569466+00:00*


## 1. Executive Summary

This report documents the **Phase 1 Corrective Review** of the NFHS-5 (2019-21) dataset for SwasthCluster.

**Key facts:**
- The dataset contains **706 rows** and **109 columns**.
- Each row represents one Indian district (**706** unique state-district combinations).
- **104** columns are classified as substantive health, contextual, or health-system indicators across **14** domains.
- **Domain Imbalance** is significant and must be addressed in Phase 2.
- **4125** values are suppressed (`*`) and **5068** are low-sample (parenthesized). These are now rigorously tracked.
- **8** columns have >30% missing values. Mean district completeness is **94.5%**.
- **Assessment**: The dataset is methodologically ready for Phase 2 feature engineering.


## 2. Phase 1 Corrective Review

This section documents the methodological corrections applied during the Phase 1 Review
to strengthen the research-design foundation prior to Phase 2 clustering.

- **Semantic Classification & Data Dictionary**: Replaced broad keywords with granular `indicator_type` fields (outcome, coverage, access, demographic, etc.). Specifically reclassified Out-of-Pocket Expenditure as a substantive health-system access metric, not statistical metadata.
- **Semantic Review (Derived & Composite Features)**: Implemented explicit logical mapping to categorize variables as raw, derived, ratio, or composite, moving away from simple keyword matching (`metadata/indicator_semantic_review.csv`).
- **Holdout Candidate Registry**: Established principles and a registry (`metadata/holdout_candidate_registry.csv`) for selecting external validation variables prior to clustering. Good holdouts must be substantive health outcomes, not used in clustering, with sufficient data coverage.
- **Low-Sample Handling**: The loader now preserves a `low_sample_flags` matrix tracking parenthesized values. Downstream sensitivity analysis will explicitly test Scenario A (retaining values) vs Scenario B (treating as missing).
- **Missingness Geographic Concentration**: Expanded analysis to measure completeness by State/UT (`metadata/missingness_by_state.csv`). Documented requirement to compare complete-case vs. KNN vs. MICE imputation iteratively during Phase 2.
- **Domain Imbalance**: Quantified domain imbalance explicitly (see Section 9). Established requirement for domain-weighting strategy exploration (raw vs equal domain weight vs PCA) in Phase 2.
- **PCA & Baseline Strategy**: Clarified that PCA is a diagnostic tool, not automatically the final clustering space. Established the baseline concept as a conventional composite-index ranking approach to contrast with multidimensional clustering.


## 3. Dataset Identification

- **File**: `datafile.csv`
- **Path**: `C:\Users\himan\OneDrive\Documents\SwasthCluster\data\raw\datafile.csv`
- **Size**: 598,132 bytes
- **Encoding**: utf-8
- **Format**: CSV (quoted fields, comma-delimited)
- **Source**: NFHS-5 (2019-21) district-level fact sheets


## 4. Dataset Dimensions

- **Rows**: 706
- **Columns**: 109
- **Memory**: 0.67 MB


### Coercion Summary

- Suppressed values (`*` → NaN): **4125**
- Parenthesized values (low-sample, parens stripped): **5068**
- Whitespace stripped: **65959**
- Coercion failures: **0**


## 5. Schema Overview

**Data type distribution:**

- `float64`: 107 columns
- `object`: 2 columns


## 6. District Identity Audit

- **District column**: `District Names`
- **State column**: `State/UT`


### District Uniqueness

- Unique states/UTs: **36**
- Unique (state, district) combos: **706**
- One row per combo: **True**

## 7. Duplicate Analysis

- Exact duplicate rows: **0**


## 8. Indicator Inventory & Semantic Review

Full data dictionary exported to `metadata/data_dictionary.csv` (109 entries).

Semantic review exported to `metadata/indicator_semantic_review.csv`.

Holdout registry exported to `metadata/holdout_candidate_registry.csv`.


### Domain Imbalance Analysis

The clustering results may be implicitly weighted if some health domains have many more indicators than others.
|    | Domain                   |   Indicator Count | Percentage   |
|---:|:-------------------------|------------------:|:-------------|
|  0 | child_health             |                19 | 18.3%        |
|  1 | maternal_health          |                16 | 15.4%        |
|  2 | reproductive_health      |                15 | 14.4%        |
|  3 | non_communicable_disease |                15 | 14.4%        |
|  4 | immunization             |                11 | 10.6%        |
|  5 | household_environment    |                 5 | 4.8%         |
|  6 | anemia                   |                 5 | 4.8%         |
|  7 | demographics             |                 4 | 3.8%         |
|  8 | substance_use            |                 4 | 3.8%         |
|  9 | literacy_education       |                 3 | 2.9%         |
| 10 | healthcare_access        |                 3 | 2.9%         |
| 11 | nutrition                |                 2 | 1.9%         |
| 12 | registration             |                 1 | 1.0%         |
| 13 | unknown                  |                 1 | 1.0%         |

> **Risk**: Raw distance-based clustering will implicitly give more weight to domains with more indicators (e.g., child health). Strategies to address this in Phase 2 include: 1) Raw weighting after standardization, 2) Equal domain weighting, 3) Domain-level PCA.

## 9. Missingness Analysis

- Columns with >30% missing: **8**


### Geographic Concentration of Missingness

Missingness by State/UT exported to `metadata/missingness_by_state.csv`.
| state                                  |   n_districts |   mean_completeness |   min_completeness |   max_completeness |   mean_missing |
|:---------------------------------------|--------------:|--------------------:|-------------------:|-------------------:|---------------:|
| Goa                                    |             2 |               86.92 |              81.31 |              92.52 |          14    |
| Sikkim                                 |             4 |               88.08 |              82.24 |              91.59 |          12.75 |
| Andaman & Nicobar Islands              |             3 |               88.16 |              80.37 |              92.52 |          12.67 |
| Kerala                                 |            14 |               90.52 |              82.24 |              94.39 |          10.14 |
| Chandigarh                             |             1 |               90.65 |              90.65 |              90.65 |          10    |
| Tamil Nadu                             |            32 |               91.85 |              81.31 |              94.39 |           8.72 |
| Puducherry                             |             4 |               92.29 |              91.59 |              92.52 |           8.25 |
| Himachal Pradesh                       |            12 |               92.44 |              90.65 |              95.33 |           8.08 |
| Andhra Pradesh                         |            13 |               93.03 |              88.79 |              95.33 |           7.46 |
| Dadra and Nagar Haveli & Daman and Diu |             3 |               93.14 |              92.52 |              94.39 |           7.33 |
| Arunachal Pradesh                      |            20 |               93.22 |              89.72 |              96.26 |           7.25 |
| Madhya Pradesh                         |            51 |               93.35 |              75.7  |              98.13 |           7.12 |
| Punjab                                 |            22 |               93.42 |              90.65 |              97.2  |           7.05 |
| Mizoram                                |             8 |               93.46 |              91.59 |              95.33 |           7    |
| Lakshadweep                            |             1 |               93.46 |              93.46 |              93.46 |           7    |

![Missingness heatmap](reports/figures/missingness_heatmap.png)


## 10. PCA Positioning and Composite Baselines

### PCA Positioning
PCA is an **exploratory diagnostic** tool in this pipeline, not automatically the final representation for clustering. It will be evaluated in Phase 2 for noise reduction and multicollinearity mitigation.

### Baseline
To evaluate whether clustering adds value, we establish a **conventional composite-index** baseline approach. The final analysis will contrast the multidimensional clusters against single-ranking composite scores to demonstrate if similarly-ranked districts have different multidimensional needs.
