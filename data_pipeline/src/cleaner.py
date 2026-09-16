"""Cleaning and enrichment for scraped books."""
from __future__ import annotations
import logging
import re
from dataclasses import asdict
from statistics import median
from typing import Iterable
import pandas as pd
from .scraper import RawBook

LOGGER = logging.getLogger(__name__)
RATING_MAP = {"One":1,"Two":2,"Three":3,"Four":4,"Five":5}
GBP_TO_INR = 105.50


def _parse_price(value: object) -> float | None:
    try:
        match = re.search(r"[-+]?\d+(?:\.\d+)?", str(value).replace(",", ""))
        return float(match.group()) if match else None
    except (TypeError, ValueError):
        return None


def _parse_rating(value: object) -> int | None:
    text = str(value).strip()
    if text in RATING_MAP: return RATING_MAP[text]
    return None


def _parse_stock(value: object) -> bool | None:
    text = str(value).strip().lower()
    if "in stock" in text: return True
    if "out of stock" in text: return False
    return None


def clean_books(raw_books: Iterable[RawBook]) -> pd.DataFrame:
    rows = [asdict(book) for book in raw_books]
    df = pd.DataFrame(rows)
    if df.empty:
        raise ValueError("No scraped rows were supplied.")
    df["price_gbp"] = df["price"].map(_parse_price)
    df["rating"] = df["star_rating"].map(_parse_rating)
    df["in_stock"] = df["availability"].map(_parse_stock)
    bad_bool = df["in_stock"].isna()
    if bad_bool.any():
        LOGGER.warning("Dropping %d rows with unparseable availability", int(bad_bool.sum()))
        df = df.loc[~bad_bool].copy()
    if df["price_gbp"].isna().any():
        med = float(df["price_gbp"].median())
        df["price_gbp"] = df["price_gbp"].fillna(med)
    if df["rating"].isna().any():
        med = int(round(df["rating"].median()))
        df["rating"] = df["rating"].fillna(med)
    df["rating"] = df["rating"].astype(int)
    df["price_gbp"] = df["price_gbp"].astype(float)
    df["in_stock"] = df["in_stock"].astype(bool)
    df["price_inr"] = df["price_gbp"] * GBP_TO_INR
    result = df[["title","price_gbp","rating","in_stock","category","price_inr"]].reset_index(drop=True)
    if not result["rating"].between(1,5).all(): raise ValueError("Rating outside 1-5 after cleaning.")
    return result
