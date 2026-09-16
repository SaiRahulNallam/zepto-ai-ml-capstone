"""Normalized SQLite persistence."""
from __future__ import annotations
import sqlite3
from pathlib import Path
import pandas as pd

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY,
    category_name TEXT UNIQUE NOT NULL
);
CREATE TABLE IF NOT EXISTS books (
    book_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    price_gbp REAL,
    price_inr REAL,
    rating INTEGER,
    in_stock INTEGER,
    category_id INTEGER NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);
"""

def create_database(db_path: str | Path, df: pd.DataFrame) -> Path:
    path = Path(db_path); path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(SCHEMA)
        conn.execute("DELETE FROM books")
        conn.execute("DELETE FROM categories")
        categories = sorted(df["category"].dropna().unique().tolist())
        conn.executemany("INSERT INTO categories(category_name) VALUES (?)", [(c,) for c in categories])
        mapping = {r[1]: r[0] for r in conn.execute("SELECT category_id, category_name FROM categories")}
        rows = []
        for _, r in df.iterrows():
            rows.append((r["title"], float(r["price_gbp"]), float(r["price_inr"]), int(r["rating"]), int(bool(r["in_stock"])), mapping[r["category"]]))
        conn.executemany("INSERT INTO books(title,price_gbp,price_inr,rating,in_stock,category_id) VALUES (?,?,?,?,?,?)", rows)
        conn.commit()
    return path


def get_connection(db_path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
