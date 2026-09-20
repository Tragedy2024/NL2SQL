"""
Global path configuration.

Single source of truth for every filesystem path in this project. All paths
are derived from the project root (the parent directory of `src/`), so the
project runs from any checkout location. Do not hardcode absolute paths
elsewhere — import from here instead.

    from config import SSA_DIR, BIRD_DEV

Requires `src/` on PYTHONPATH (see README.md), which the documented setup
already provides:

    export PYTHONPATH="<项目根>/src;<项目根>/vendor/MAC-SQL"
"""
import os

# Project root = parent of this file's directory (src/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ============================================================
# Project directories
# ============================================================
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
VENDOR_DIR = os.path.join(PROJECT_ROOT, "vendor", "MAC-SQL")
CONFIG_DIR = os.path.join(PROJECT_ROOT, "config")
SSA_DIR = os.path.join(CONFIG_DIR, "ssa")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")
EXPERIMENTS_DIR = os.path.join(PROJECT_ROOT, "experiments")
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, "outputs")

# ============================================================
# Datasets
# ============================================================
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

# BIRD dev (1,534 queries)
BIRD_DIR = os.path.join(DATA_DIR, "bird-dev", "dev_20240627")
BIRD_DB_PATH = os.path.join(BIRD_DIR, "dev_databases")
BIRD_TABLES = os.path.join(BIRD_DIR, "dev_tables.json")
BIRD_DEV = os.path.join(BIRD_DIR, "dev.json")
BIRD_COMPLEX = os.path.join(DATA_DIR, "bird-dev", "complex_queries.json")

# Spider 1.0 dev (1,034 queries)
SPIDER_DIR = os.path.join(DATA_DIR, "spider1.0")
SPIDER_DB_PATH = os.path.join(SPIDER_DIR, "database")
SPIDER_TABLES = os.path.join(SPIDER_DIR, "tables.json")
SPIDER_DEV = os.path.join(SPIDER_DIR, "dev.json")

# ============================================================
# Convenience: result file paths
# ============================================================
def results_path(group: str, name: str) -> str:
    """Path to a result file, e.g. results_path('rq1', 'rq1_bird_fewshot_results.jsonl')."""
    return os.path.join(RESULTS_DIR, group, name)


# Backward-compatible aliases (BIRD is the default dataset)
DB_PATH = BIRD_DB_PATH
TABLES_JSON = BIRD_TABLES
DEV_JSON = BIRD_DEV
COMPLEX_JSON = BIRD_COMPLEX
