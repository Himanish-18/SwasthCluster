# SwasthCluster Phase 1 — Data Audit

*Generated: 2026-09-11T16:13:25.898172+00:00*


## 1. Executive Summary

This report documents the Phase 1 data audit of the NFHS-5 (2019-21) district-level
dataset for the SwasthCluster project.

**Key facts:**
- The dataset contains **706 rows** and **109 columns**.
- Each row represents one Indian district (confirmed: **706** unique
  state-district combinations, one row per combination).
- **103** columns are classified as health/nutrition indicators across
  **14** domains.
- **4125** values are suppressed (`*`, <25 cases) and
  **5068** are flagged as low-sample (parenthesized).
- **8** columns have >30% missing values.
- Mean district completeness is **94.5%**.
- **Assessment**: The dataset is suitable for district-level clustering
  **with conditions** (see Section 15).


## 2. Dataset Identification

- **File**: `datafile.csv`
- **Path**: `C:\Users\himan\OneDrive\Documents\SwasthCluster\data\raw\datafile.csv`
- **Size**: 598,132 bytes
- **Encoding**: utf-8
- **Format**: CSV (quoted fields, comma-delimited)
- **Source**: NFHS-5 (2019-21) district-level fact sheets


## 3. Dataset Dimensions

- **Rows**: 706
- **Columns**: 109
- **Memory**: 0.67 MB


### Coercion Summary

- Suppressed values (`*` → NaN): **4125**
- Parenthesized values (low-sample, parens stripped): **5068**
- Whitespace stripped: **65959**
- Coercion failures: **0**


## 4. Schema Overview

**Data type distribution:**

- `float64`: 107 columns
- `object`: 2 columns

**Column profile (first 30 columns):**

| column                                                                                                       | dtype   |   unique_count |   unique_pct |   null_count |   null_pct |
|:-------------------------------------------------------------------------------------------------------------|:--------|---------------:|-------------:|-------------:|-----------:|
| District Names                                                                                               | object  |            698 |        98.87 |            0 |       0    |
| State/UT                                                                                                     | object  |             36 |         5.1  |            0 |       0    |
| Number of Households surveyed                                                                                | float64 |            185 |        26.2  |            0 |       0    |
| Number of Women age 15-49 years interviewed                                                                  | float64 |            435 |        61.61 |            0 |       0    |
| Number of Men age 15-54 years interviewed                                                                    | float64 |            146 |        20.68 |            0 |       0    |
| Female population age 6 years and above who ever attended school (%)                                         | float64 |            336 |        47.59 |            0 |       0    |
| Population below age 15 years (%)                                                                            | float64 |            206 |        29.18 |            0 |       0    |
| Sex ratio of the total population (females per 1,000 males)                                                  | float64 |            267 |        37.82 |            0 |       0    |
| Sex ratio at birth for children born in the last five years (females per 1,000 males)                        | float64 |            350 |        49.58 |            0 |       0    |
| Children under age 5 years whose birth was registered with the civil authority (%)                           | float64 |            239 |        33.85 |            0 |       0    |
| Deaths in the last 3 years registered with the civil authority (%)                                           | float64 |            436 |        61.76 |            1 |       0.14 |
| Population living in households with electricity (%)                                                         | float64 |            123 |        17.42 |            0 |       0    |
| Population living in households with an improved drinking-water source1 (%)                                  | float64 |            197 |        27.9  |            0 |       0    |
| Population living in households that use an improved sanitation facility2 (%)                                | float64 |            380 |        53.82 |            0 |       0    |
| Households using clean fuel for cooking3 (%)                                                                 | float64 |            489 |        69.26 |            0 |       0    |
| Households using iodized salt (%)                                                                            | float64 |            166 |        23.51 |            0 |       0    |
| Households with any usual member covered under a health insurance/financing scheme (%)                       | float64 |            470 |        66.57 |            0 |       0    |
| Children age 5 years who attended pre-primary school during the school year 2019-20 (%)                      | float64 |            282 |        39.94 |            3 |       0.42 |
| Women (age 15-49) who are literate4 (%)                                                                      | float64 |            361 |        51.13 |            0 |       0    |
| Women (age 15-49)  with 10 or more years of schooling (%)                                                    | float64 |            387 |        54.82 |            0 |       0    |
| Women age 20-24 years married before age 18 years (%)                                                        | float64 |            355 |        50.28 |            0 |       0    |
| Births in the 5 years preceding the survey that are third or higher order (%)                                | float64 |             70 |         9.92 |            1 |       0.14 |
| Women age 15-19 years who were already mothers or pregnant at the time of the survey (%)                     | float64 |            170 |        24.08 |            0 |       0    |
| Women age 15-24 years who use hygienic methods of protection during their menstrual period5 (%)              | float64 |            376 |        53.26 |            0 |       0    |
| Current Use of Family Planning Methods (Currently Married Women Age 15-49  years) - Any method6 (%)          | float64 |            344 |        48.73 |            0 |       0    |
| Current Use of Family Planning Methods (Currently Married Women Age 15-49  years) - Any modern method6 (%)   | float64 |            375 |        53.12 |            0 |       0    |
| Current Use of Family Planning Methods (Currently Married Women Age 15-49  years) - Female sterilization (%) | float64 |            442 |        62.61 |            0 |       0    |
| Current Use of Family Planning Methods (Currently Married Women Age 15-49  years) - Male sterilization (%)   | float64 |             54 |         7.65 |            0 |       0    |
| Current Use of Family Planning Methods (Currently Married Women Age 15-49  years) - IUD/PPIUD (%)            | float64 |            106 |        15.01 |            0 |       0    |
| Current Use of Family Planning Methods (Currently Married Women Age 15-49  years) - Pill (%)                 | float64 |            180 |        25.5  |            0 |       0    |

- Constant numeric columns: **0**
- Near-constant numeric columns: **0**

**Categorical columns:**

| column         |   unique_count |   unique_after_lower_strip |   capitalisation_inconsistencies |   leading_trailing_whitespace |   blank_strings |   rare_categories_count | top_3_values                         |
|:---------------|---------------:|---------------------------:|---------------------------------:|------------------------------:|----------------:|------------------------:|:-------------------------------------|
| District Names |            698 |                        698 |                                0 |                             0 |               0 |                     698 | Aurangabad, Balrampur, Raigarh       |
| State/UT       |             36 |                         36 |                                0 |                             0 |               0 |                       4 | Uttar Pradesh, Madhya Pradesh, Bihar |


## 5. District Identity Audit

- **District column**: `District Names`
- **State column**: `State/UT`

**`District Names`**:
  - Data type: `object`
  - Unique count: 698
  - Null count: 0
  - Uniqueness ratio: 0.9887
  - Examples: ['Nicobars', 'North & Middle Andaman', 'South Andaman', 'Srikakulam', 'Vizianagaram']

**`State/UT`**:
  - Data type: `object`
  - Unique count: 36
  - Null count: 0
  - Uniqueness ratio: 0.051
  - Examples: ['Andaman & Nicobar Islands', 'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar']


### District Uniqueness

- Total rows: **706**
- Unique districts (by name only): **698**
- Unique states/UTs: **36**
- Unique (state, district) combos: **706**
- One row per combo: **True**
- Max rows per combo: **1**

**District names appearing in multiple states: 8**

|    | District Names   |   n_states | State/UT         |
|---:|:-----------------|-----------:|:-----------------|
|  0 | Aurangabad       |          2 | Bihar            |
|  1 | Aurangabad       |          2 | Maharastra       |
|  2 | Balrampur        |          2 | Chhattisgarh     |
|  3 | Balrampur        |          2 | Uttar Pradesh    |
|  4 | Bijapur          |          2 | Chhattisgarh     |
|  5 | Bijapur          |          2 | Karnataka        |
|  6 | Bilaspur         |          2 | Chhattisgarh     |
|  7 | Bilaspur         |          2 | Himachal Pradesh |
|  8 | Chandel          |          2 | Manipur          |
|  9 | Chandel          |          2 | Mizoram          |
| 10 | Hamirpur         |          2 | Himachal Pradesh |
| 11 | Hamirpur         |          2 | Uttar Pradesh    |
| 12 | Pratapgarh       |          2 | Rajasthan        |
| 13 | Pratapgarh       |          2 | Uttar Pradesh    |
| 14 | Raigarh          |          2 | Chhattisgarh     |
| 15 | Raigarh          |          2 | Maharastra       |


## 6. State-District Consistency

- Unique state names (raw): **36**
- Unique state names (normalised): **36**

No capitalisation inconsistencies found in state names.

No whitespace issues in state names.


**All states/UTs:**

  - Andaman & Nicobar Islands
  - Andhra Pradesh
  - Arunachal Pradesh
  - Assam
  - Bihar
  - Chandigarh
  - Chhattisgarh
  - Dadra and Nagar Haveli & Daman and Diu
  - Goa
  - Gujarat
  - Haryana
  - Himachal Pradesh
  - Jammu & Kashmir
  - Jharkhand
  - Karnataka
  - Kerala
  - Ladakh
  - Lakshadweep
  - Madhya Pradesh
  - Maharastra
  - Manipur
  - Meghalaya
  - Mizoram
  - NCT of Delhi
  - Nagaland
  - Odisha
  - Puducherry
  - Punjab
  - Rajasthan
  - Sikkim
  - Tamil Nadu
  - Telangana
  - Tripura
  - Uttar Pradesh
  - Uttarakhand
  - West Bengal

- Unique district names (raw): **698**
- Unique district names (stripped): **698**
- Whitespace issues in district names: **0**


## 7. Duplicate Analysis

- Exact duplicate rows: **0** (0.0%)

- District names appearing more than once: **8**
  (These may be legitimate — same district name in different states.)

| District Name | Occurrences |
|---------------|-------------|
| Aurangabad | 2 |
| Balrampur | 2 |
| Raigarh | 2 |
| Hamirpur | 2 |
| Pratapgarh | 2 |
| Bilaspur | 2 |
| Chandel | 2 |
| Bijapur | 2 |

- Duplicate (state, district) combos: **0**


## 8. Indicator Inventory

**Column role distribution:**

- `HEALTH_INDICATOR`: 103
- `SAMPLE_METADATA`: 3
- `IDENTIFIER`: 2
- `STATISTICAL_METADATA`: 1

**Health indicator domains:**

- `child_health`: 19
- `reproductive_health`: 15
- `maternal_health`: 15
- `non_communicable_disease`: 15
- `immunization`: 11
- `household_environment`: 5
- `anemia`: 5
- `demographics`: 4
- `substance_use`: 4
- `literacy_education`: 3
- `healthcare_access`: 3
- `nutrition`: 2
- `registration`: 1
- `unknown`: 1

Full data dictionary exported to `metadata/data_dictionary.csv` (109 entries).


## 9. Missingness Analysis

- Columns with zero missing: **80**
- Columns with any missing: **29**
- Columns with >30% missing: **8**

**Top 25 columns by missingness:**

|                                                                                                                                                           |   missing_count |   missing_pct |
|:----------------------------------------------------------------------------------------------------------------------------------------------------------|----------------:|--------------:|
| Non-breastfeeding children age 6-23 months receiving an adequate diet16, 17 (%)                                                                           |             643 |         91.08 |
| Children age 6-8 months receiving solid or semi-solid food and breastmilk16 (%)                                                                           |             642 |         90.93 |
| Children swith diarrhoea in the 2 weeks preceding the survey taken to a health facility or health provider (Children under age 5 years) (%)               |             492 |         69.69 |
| Children with diarrhoea in the 2 weeks preceding the survey who received zinc (Children under age 5 years) (%)                                            |             492 |         69.69 |
| Children with diarrhoea in the 2 weeks preceding the survey who received oral rehydration salts (ORS) (Children under age 5 years) (%)                    |             492 |         69.69 |
| Children born at home who were taken to a health facility for a check-up within 24 hours of birth (for last birth in the 5 years before the survey} (%)   |             422 |         59.77 |
| Children under age 6 months exclusively breastfed16 (%)                                                                                                   |             261 |         36.97 |
| Children with fever or symptoms of ARI in the 2 weeks preceding the survey taken to a health facility or health provider (Children under age 5 years) (%) |             224 |         31.73 |
| Births in a private health facility that were delivered by caesarean section (in the 5 years before the survey) (%)                                       |             150 |         21.25 |
| Pregnant women age 15-49 years who are anaemic (<11.0 g/dl)22 (%)                                                                                         |             134 |         18.98 |
| Children age 12-23 months fully vaccinated based on information from vaccination card only12 (%)                                                          |              22 |          3.12 |
| Children age 12-23 months who received most of their vaccinations in a public health facility (%)                                                         |              16 |          2.27 |
| Children age 12-23 months who received most of their vaccinations in a private health facility (%)                                                        |              16 |          2.27 |
| Children age 12-23 months fully vaccinated based on information from either vaccination card or mother's recall11 (%)                                     |              13 |          1.84 |
| Children age 12-23 months who have received BCG (%)                                                                                                       |              13 |          1.84 |
| Children age 12-23 months who have received 3 doses of polio vaccine13 (%)                                                                                |              13 |          1.84 |
| Children age 12-23 months who have received 3 doses of penta or DPT vaccine (%)                                                                           |              13 |          1.84 |
| Children age 12-23 months who have received the first dose of measles-containing vaccine (MCV) (%)                                                        |              13 |          1.84 |
| Children age 24-35 months who have received a second dose of measles-containing vaccine (MCV) (%)                                                         |              13 |          1.84 |
| Children age 12-23 months who have received 3 doses of rotavirus vaccine14 (%)                                                                            |              13 |          1.84 |
| Children age 12-23 months who have received 3 doses of penta or hepatitis B vaccine (%)                                                                   |              13 |          1.84 |
| Breastfeeding children age 6-23 months receiving an adequate diet16, 17  (%)                                                                              |               5 |          0.71 |
| Children age 5 years who attended pre-primary school during the school year 2019-20 (%)                                                                   |               3 |          0.42 |
| Current users ever told about side effects of current method of family planning8 (%)                                                                      |               2 |          0.28 |
| Children age 9-35 months who received a vitamin A dose in the last 6 months (%)                                                                           |               1 |          0.14 |


### District-level Missingness

- Fully complete districts: **18** / 706
- Districts with <70% completeness: **0**
- Minimum completeness: **75.7%**
- Mean completeness: **94.5%**


### Geographic Concentration of Missingness

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

![Missingness bar chart](reports/figures/missingness_bar.png)

![Missingness heatmap](reports/figures/missingness_heatmap.png)


## 10. Value/Range Validation

- Columns validated: **107**
- Columns with values outside expected range: **0**

All validated columns fall within expected ranges.



## 11. Distribution Analysis

- Numeric columns analysed: **107**
- Highly skewed (|skew| > 2): **17**
- Near-zero variance: **0**

**Highly skewed columns (top 20):**

| column                                                                                                                                              |   n_valid |      mean |   median |       std |   skewness |
|:----------------------------------------------------------------------------------------------------------------------------------------------------|----------:|----------:|---------:|----------:|-----------:|
| Current Use of Family Planning Methods (Currently Married Women Age 15-49  years) - Male sterilization (%)                                          |       706 |    0.52   |      0.1 |    1.6213 |     6.3514 |
| Women (age 30-49 years) Ever undergone an oral cavity examination for oral cancer (%)                                                               |       706 |    0.7059 |      0.3 |    1.4689 |     5.7454 |
| Women (age 30-49 years) Ever undergone a breast examination for breast cancer (%)                                                                   |       706 |    0.6576 |      0.2 |    1.5696 |     5.0253 |
| Current Use of Family Planning Methods (Currently Married Women Age 15-49  years) - Injectables (%)                                                 |       706 |    0.63   |      0.3 |    1.092  |     4.6307 |
| Current Use of Family Planning Methods (Currently Married Women Age 15-49  years) - IUD/PPIUD (%)                                                   |       706 |    2.887  |      1.9 |    3.432  |     4.0889 |
| Number of Households surveyed                                                                                                                       |       706 |  900.482  |    908   |   69.3203 |    -3.8278 |
| Registered pregnancies for which the mother received a Mother and Child Protection (MCP) card (for last birth in the 5 years before the survey) (%) |       706 |   96.188  |     97.6 |    4.5947 |    -3.7405 |
| Women (age 30-49 years) Ever undergone a screening test for cervical cancer (%)                                                                     |       706 |    1.5744 |      0.6 |    2.7748 |     3.5972 |
| Women age 15 years and above who consume alcohol (%)                                                                                                |       706 |    2.9224 |      0.5 |    6.0838 |     3.1153 |
| Population living in households with electricity (%)                                                                                                |       706 |   97.0017 |     98.7 |    4.3547 |    -2.973  |
| Unmet need for spacing (Currently Married Women Age 15-49  years)7 (%)                                                                              |       706 |    4.2924 |      3.7 |    2.7837 |     2.7767 |
| Households using iodized salt (%)                                                                                                                   |       706 |   95.1296 |     97   |    5.4833 |    -2.6894 |
| Population living in households with an improved drinking-water source1 (%)                                                                         |       706 |   93.7229 |     97   |    8.7182 |    -2.6349 |
| Current Use of Family Planning Methods (Currently Married Women Age 15-49  years) - Pill (%)                                                        |       706 |    5.6067 |      2.5 |    8.0703 |     2.5868 |
| Average out-of-pocket expenditure per delivery in a public health facility (for last birth in the 5 years before the survey) (Rs.)                  |       705 | 3529.35   |   2830   | 2525.69   |     2.3302 |
| Children age 12-23 months who received most of their vaccinations in a private health facility (%)                                                  |       690 |    3.2055 |      1.6 |    4.496  |     2.2586 |
| Women age 15 years and above who use any kind of tobacco (%)                                                                                        |       706 |   11.6222 |      7.7 |   11.9501 |     2.2011 |

![Distribution overview](reports/figures/distribution_overview.png)


## 12. Non-Analytical / Metadata Columns

**Column classification:**

|    | column                                                                                                                                                                           | role                 | rationale                                             |
|---:|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------------------|:------------------------------------------------------|
|  0 | District Names                                                                                                                                                                   | IDENTIFIER           | Name contains district/state keyword                  |
|  1 | State/UT                                                                                                                                                                         | IDENTIFIER           | Name contains district/state keyword                  |
|  2 | Number of Households surveyed                                                                                                                                                    | SAMPLE_METADATA      | Survey sample size variable                           |
|  3 | Number of Women age 15-49 years interviewed                                                                                                                                      | SAMPLE_METADATA      | Survey sample size variable                           |
|  4 | Number of Men age 15-54 years interviewed                                                                                                                                        | SAMPLE_METADATA      | Survey sample size variable                           |
|  5 | Female population age 6 years and above who ever attended school (%)                                                                                                             | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
|  6 | Population below age 15 years (%)                                                                                                                                                | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
|  7 | Sex ratio of the total population (females per 1,000 males)                                                                                                                      | HEALTH_INDICATOR     | Sex ratio (per 1,000 males) — different scale from %  |
|  8 | Sex ratio at birth for children born in the last five years (females per 1,000 males)                                                                                            | HEALTH_INDICATOR     | Sex ratio (per 1,000 males) — different scale from %  |
|  9 | Children under age 5 years whose birth was registered with the civil authority (%)                                                                                               | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 10 | Deaths in the last 3 years registered with the civil authority (%)                                                                                                               | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 11 | Population living in households with electricity (%)                                                                                                                             | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 12 | Population living in households with an improved drinking-water source1 (%)                                                                                                      | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 13 | Population living in households that use an improved sanitation facility2 (%)                                                                                                    | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 14 | Households using clean fuel for cooking3 (%)                                                                                                                                     | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 15 | Households using iodized salt (%)                                                                                                                                                | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 16 | Households with any usual member covered under a health insurance/financing scheme (%)                                                                                           | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 17 | Children age 5 years who attended pre-primary school during the school year 2019-20 (%)                                                                                          | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 18 | Women (age 15-49) who are literate4 (%)                                                                                                                                          | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 19 | Women (age 15-49)  with 10 or more years of schooling (%)                                                                                                                        | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 20 | Women age 20-24 years married before age 18 years (%)                                                                                                                            | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 21 | Births in the 5 years preceding the survey that are third or higher order (%)                                                                                                    | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 22 | Women age 15-19 years who were already mothers or pregnant at the time of the survey (%)                                                                                         | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 23 | Women age 15-24 years who use hygienic methods of protection during their menstrual period5 (%)                                                                                  | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 24 | Current Use of Family Planning Methods (Currently Married Women Age 15-49  years) - Any method6 (%)                                                                              | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 25 | Current Use of Family Planning Methods (Currently Married Women Age 15-49  years) - Any modern method6 (%)                                                                       | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 26 | Current Use of Family Planning Methods (Currently Married Women Age 15-49  years) - Female sterilization (%)                                                                     | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 27 | Current Use of Family Planning Methods (Currently Married Women Age 15-49  years) - Male sterilization (%)                                                                       | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 28 | Current Use of Family Planning Methods (Currently Married Women Age 15-49  years) - IUD/PPIUD (%)                                                                                | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 29 | Current Use of Family Planning Methods (Currently Married Women Age 15-49  years) - Pill (%)                                                                                     | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 30 | Current Use of Family Planning Methods (Currently Married Women Age 15-49  years) - Condom (%)                                                                                   | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 31 | Current Use of Family Planning Methods (Currently Married Women Age 15-49  years) - Injectables (%)                                                                              | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 32 | Total Unmet need for Family Planning (Currently Married Women Age 15-49  years)7 (%)                                                                                             | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 33 | Unmet need for spacing (Currently Married Women Age 15-49  years)7 (%)                                                                                                           | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 34 | Health worker ever talked to female non-users about family planning (%)                                                                                                          | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 35 | Current users ever told about side effects of current method of family planning8 (%)                                                                                             | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 36 | Mothers who had an antenatal check-up in the first trimester  (for last birth in the 5 years before the survey) (%)                                                              | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 37 | Mothers who had at least 4 antenatal care visits  (for last birth in the 5 years before the survey) (%)                                                                          | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 38 | Mothers whose last birth was protected against neonatal tetanus (for last birth in the 5 years before the survey)9 (%)                                                           | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 39 | Mothers who consumed iron folic acid for 100 days or more when they were pregnant (for last birth in the 5 years before the survey) (%)                                          | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 40 | Mothers who consumed iron folic acid for 180 days or more when they were pregnant (for last birth in the 5 years before the survey} (%)                                          | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 41 | Registered pregnancies for which the mother received a Mother and Child Protection (MCP) card (for last birth in the 5 years before the survey) (%)                              | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 42 | Mothers who received postnatal care from a doctor/nurse/LHV/ANM/midwife/other health personnel within 2 days of delivery (for last birth in the 5 years before the survey) (%)   | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 43 | Average out-of-pocket expenditure per delivery in a public health facility (for last birth in the 5 years before the survey) (Rs.)                                               | STATISTICAL_METADATA | Monetary expenditure in Rupees — different unit/scale |
| 44 | Children born at home who were taken to a health facility for a check-up within 24 hours of birth (for last birth in the 5 years before the survey} (%)                          | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 45 | Children who received postnatal care from a doctor/nurse/LHV/ANM/midwife/ other health personnel within 2 days of delivery (for last birth in the 5 years before the survey) (%) | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 46 | Institutional births (in the 5 years before the survey) (%)                                                                                                                      | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 47 | Institutional births in public facility (in the 5 years before the survey) (%)                                                                                                   | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 48 | Home births that were conducted by skilled health personnel  (in the 5 years before the survey)10 (%)                                                                            | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 49 | Births attended by skilled health personnel (in the 5 years before the survey)10 (%)                                                                                             | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 50 | Births delivered by caesarean section (in the 5 years before the survey) (%)                                                                                                     | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 51 | Births in a private health facility that were delivered by caesarean section (in the 5 years before the survey) (%)                                                              | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 52 | Births in a public health facility that were delivered by caesarean section (in the 5 years before the survey) (%)                                                               | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 53 | Children age 12-23 months fully vaccinated based on information from either vaccination card or mother's recall11 (%)                                                            | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 54 | Children age 12-23 months fully vaccinated based on information from vaccination card only12 (%)                                                                                 | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 55 | Children age 12-23 months who have received BCG (%)                                                                                                                              | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 56 | Children age 12-23 months who have received 3 doses of polio vaccine13 (%)                                                                                                       | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 57 | Children age 12-23 months who have received 3 doses of penta or DPT vaccine (%)                                                                                                  | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 58 | Children age 12-23 months who have received the first dose of measles-containing vaccine (MCV) (%)                                                                               | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |
| 59 | Children age 24-35 months who have received a second dose of measles-containing vaccine (MCV) (%)                                                                                | HEALTH_INDICATOR     | Percentage-based health/nutrition indicator           |

Columns **not** classified as `HEALTH_INDICATOR`: **6**

- `District Names` → **IDENTIFIER** — Name contains district/state keyword
- `State/UT` → **IDENTIFIER** — Name contains district/state keyword
- `Number of Households surveyed` → **SAMPLE_METADATA** — Survey sample size variable
- `Number of Women age 15-49 years interviewed` → **SAMPLE_METADATA** — Survey sample size variable
- `Number of Men age 15-54 years interviewed` → **SAMPLE_METADATA** — Survey sample size variable
- `Average out-of-pocket expenditure per delivery in a public health facility (for last birth in the 5 years before the survey) (Rs.)` → **STATISTICAL_METADATA** — Monetary expenditure in Rupees — different unit/scale


## 13. Composite / Derived Feature Investigation

The dataset was inspected for composite health scores, wealth indices,
rankings, or pre-computed aggregate indices.

**Findings:**

The following columns contain keywords suggestive of composite/derived scores:

- `Sex ratio of the total population (females per 1,000 males)` (keyword: `total`)
- `Total Unmet need for Family Planning (Currently Married Women Age 15-49  years)7 (%)` (keyword: `total`)
- `Total children age 6-23 months receiving an adequate diet16, 17  (%)` (keyword: `total`)
- `Women (age 15-49 years) whose Body Mass Index (BMI) is below normal (BMI <18.5 kg/m2)21 (%)` (keyword: `index`)

> **Note**: These require careful review in Phase 2 to determine whether
> they are aggregated/derived and should be excluded from clustering to
> avoid circularity with the project's goal of creating *new* groupings.


## 14. Data Quality Issues

1. **Suppressed values**: 4125 cells marked `*` (NFHS convention: <25 unweighted cases). These are NaN in the loaded data.

2. **Low-sample-size values**: 5068 cells were parenthesized (25-49 unweighted cases per NFHS convention). Numeric values were extracted but may have higher uncertainty.

3. **High missingness**: 8 columns have >30% missing values. This will affect the usable indicator count for clustering.



## 15. Dataset Suitability

**Assessment: YES, WITH CONDITIONS**

Evidence:

1. **Usable district observations**: 706 unique (state, district) combinations identified.
2. **District identity reliability**: One row per (state, district) — confirmed.
3. **Health/nutrition indicators**: 103 columns classified as HEALTH_INDICATOR, spanning 14 domains.
4. **Missingness**: Mean district completeness 94.5%. 8 columns have >30% missing — imputation strategy needed.
5. **Duplicates**: 0 exact duplicate rows.
6. **Geographic identifiers**: District and state columns detected and validated.
7. **NFHS special values**: 4125 suppressed (`*`) and 5068 low-sample parenthesized values affect data density.

**Conditions for Phase 2:**

- Decide handling strategy for suppressed (`*`) values (currently NaN).
- Decide whether parenthesized (low-n) values are reliable enough to include.
- Address high-missingness columns (drop vs. impute).
- Determine appropriate imputation strategy.
- Investigate and resolve any range violations.
- Standardise district/state names (strip whitespace).


## 16. Risks and Open Questions

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


## 17. Recommendations for Phase 2

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


## 18. Reproducibility Information

- **Generated at**: 2026-09-11T16:13:32.449656+00:00
- **Duration**: 6.6s
- **Python**: 3.11.2 (tags/v3.11.2:878ead1, Feb  7 2023, 16:38:35) [MSC v.1934 64 bit (AMD64)]
- **Command**: `python scripts/run_phase1_audit.py`
- **Dataset**: `datafile.csv` (706 rows × 109 cols)
