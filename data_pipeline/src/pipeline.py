"""End-to-end data pipeline runner."""
from __future__ import annotations
import logging
from pathlib import Path
import pandas as pd
from .scraper import scrape_categories
from .cleaner import clean_books, GBP_TO_INR
from .database import create_database
from .queries import execute_and_record, pandas_join_equivalence

LOGGER = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]

def run(output_root: Path = ROOT) -> dict:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    raw = scrape_categories()
    clean = clean_books(raw)
    data_path = output_root / "data" / "books_clean.csv"
    db_path = output_root / "database" / "zepto_books.db"
    data_path.parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv(data_path, index=False)
    create_database(db_path, clean)
    result_path = output_root / "sql" / "query_outputs.md"
    results = execute_and_record(db_path, result_path)
    sql_df, pandas_df, equivalent = pandas_join_equivalence(db_path)
    validation = {
        "rows": len(clean), "categories": clean["category"].nunique(),
        "gbp_to_inr": GBP_TO_INR, "join_equivalent": equivalent,
        "query_rows": {k: len(v) for k,v in results.items()}
    }
    (output_root/"outputs").mkdir(exist_ok=True)
    pd.DataFrame([validation]).to_csv(output_root/"outputs"/"validation_summary.csv", index=False)
    return validation

if __name__ == "__main__":
    print(run())
