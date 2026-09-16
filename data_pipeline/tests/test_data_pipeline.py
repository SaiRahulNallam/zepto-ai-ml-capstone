import sqlite3
import pandas as pd
from data_pipeline.src.cleaner import clean_books, GBP_TO_INR
from data_pipeline.src.scraper import RawBook, _parse_listing
from data_pipeline.src.database import create_database
from data_pipeline.src.queries import QUERIES, pandas_join_equivalence


def sample_df():
    raw=[RawBook(f"Book {i}", f"£{10+i}", ["One","Two","Three","Four","Five"][i%5], "In stock", ["Travel","Mystery","History"][i%3]) for i in range(60)]
    return clean_books(raw)


def test_scraper_output_structure():
    html='<article class="product_pod"><h3><a title="X">X</a></h3><p class="price_color">&pound;10.00</p><p class="star-rating Three"></p><p class="instock availability">In stock</p></article>'
    out=_parse_listing(html, "Test")
    assert out[0].title == "X"
    assert out[0].price == "£10.00"


def test_cleaning_and_currency():
    df=sample_df(); assert len(df)==60
    assert df["rating"].dtype.kind in "iu"
    assert df["in_stock"].dtype == bool
    assert (df["price_inr"] == df["price_gbp"] * GBP_TO_INR).all()


def test_database_and_equivalence(tmp_path):
    df=sample_df(); db=tmp_path/"books.db"; create_database(db, df)
    with sqlite3.connect(db) as conn:
        assert conn.execute("SELECT COUNT(*) FROM books").fetchone()[0] == 60
        assert conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0] == 3
        fk=conn.execute("PRAGMA foreign_key_list(books)").fetchall(); assert fk
    sql_df, pd_df, ok=pandas_join_equivalence(db)
    assert ok
    assert set(QUERIES) == {"q1_where","q2_order_limit","q3_distinct","q4_between","q5_join"}
