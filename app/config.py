from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "outputs"
CHARTS_DIR = OUTPUT_DIR / "charts"
REPORTS_DIR = OUTPUT_DIR / "reports"
DATABASE_DIR = OUTPUT_DIR / "database"
DB_PATH = DATABASE_DIR / "sheet_sage.db"

DEFAULT_TOP_N = 10
MAX_CATEGORICAL_UNIQUES = 30
NULL_ALERT_THRESHOLD = 0.30
HIGH_NULL_ALERT_THRESHOLD = 0.50

for folder in [OUTPUT_DIR, CHARTS_DIR, REPORTS_DIR, DATABASE_DIR]:
    folder.mkdir(parents=True, exist_ok=True)