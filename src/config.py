"""
SwasthCluster — centralised paths and constants.

All paths are relative to PROJECT_ROOT so the project works regardless
of where it is cloned.
"""

from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent  # SwasthCluster/

DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_INTERIM_DIR = PROJECT_ROOT / "data" / "interim"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

RAW_DATASET_FILENAME = "datafile.csv"
RAW_DATASET_PATH = DATA_RAW_DIR / RAW_DATASET_FILENAME

REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

METADATA_DIR = PROJECT_ROOT / "metadata"

# ── NFHS special-value markers ─────────────────────────────────────────
NFHS_SUPPRESSED_MARKER = "*"  # value suppressed due to <25 unweighted cases
NFHS_PAREN_PATTERN = r"^\((.+)\)$"  # (value) → based on 25-49 cases
