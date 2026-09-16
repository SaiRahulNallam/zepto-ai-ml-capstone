"""Required SQL queries and result capture."""
from __future__ import annotations
from pathlib import Path
import sqlite3
import pandas as pd

QUERIES = {
    "q1_where": "SELECT title, price_gbp FROM books WHERE rating >= 4 ORDER BY price_gbp DESC;",
    "q2_order_limit": "SELECT title, price_inr FROM books ORDER BY price_inr DESC LIMIT 10;",
    "q3_distinct": "SELECT DISTINCT category FROM (SELECT c.category_name AS category FROM books b JOIN categories c ON b.category_id = c.category_id);",
    "q4_between": "SELECT title, rating, price_gbp FROM books WHERE price_gbp BETWEEN 20 AND 40 ORDER BY price_gbp;",
    "q5_join": "SELECT c.category_name AS category, b.title, b.rating, b.price_gbp FROM books b JOIN categories c ON b.category_id = c.category_id ORDER BY c.category_name, b.rating DESC, b.title LIMIT 30;",
}

def execute_and_record(db_path: str | Path, output_path: str | Path) -> dict[str, pd.DataFrame]:
    output = Path(output_path); output.parent.mkdir(parents=True, exist_ok=True)
    results = {}
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        with output.open("w", encoding="utf-8") as f:
            for name, sql in QUERIES.items():
                df = pd.read_sql_query(sql, conn)
                results[name] = df
                f.write(f"## {name}\n\n```sql\n{sql}\n```\n\n")
                f.write(df.to_markdown(index=False))
                f.write("\n\n")
    return results


def pandas_join_equivalence(db_path: str | Path) -> tuple[pd.DataFrame, pd.DataFrame, bool]:
    with sqlite3.connect(db_path) as conn:
        sql = QUERIES["q5_join"]
        sql_df = pd.read_sql_query(sql, conn)
        books = pd.read_sql_query("SELECT * FROM books", conn)
        categories = pd.read_sql_query("SELECT * FROM categories", conn)
    merged = books.merge(categories, on="category_id", how="inner")
    merged = merged.rename(columns={"category_name":"category"})
    merged = merged[["category","title","rating","price_gbp"]].sort_values(["category","rating","title"], ascending=[True,False,True]).head(30).reset_index(drop=True)
    eq = sql_df.reset_index(drop=True).equals(merged)
    return sql_df.reset_index(drop=True), merged, eq
