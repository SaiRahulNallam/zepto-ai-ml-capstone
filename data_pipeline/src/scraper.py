"""Web scraper for books.toscrape.com."""
from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Iterable
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

LOGGER = logging.getLogger(__name__)
BASE_URL = "https://books.toscrape.com/"
# These are the current category paths published by books.toscrape.com.
# Historical Fiction uses *_4* (not *_20*) on the live site.
CATEGORY_URLS = [
    urljoin(BASE_URL, "catalogue/category/books/travel_2/index.html"),
    urljoin(BASE_URL, "catalogue/category/books/mystery_3/index.html"),
    urljoin(BASE_URL, "catalogue/category/books/historical-fiction_4/index.html"),
]

@dataclass(frozen=True)
class RawBook:
    title: str
    price: str
    star_rating: str
    availability: str
    category: str


def _fetch(url: str, timeout: int = 20) -> str:
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(f"Failed to fetch {url}: {exc}") from exc
    return response.text


def _parse_listing(html: str, category: str) -> list[RawBook]:
    soup = BeautifulSoup(html, "html.parser")
    books: list[RawBook] = []
    for article in soup.select("article.product_pod"):
        title_tag = article.select_one("h3 a")
        price_tag = article.select_one("p.price_color")
        rating_tag = article.select_one("p.star-rating")
        availability_tag = article.select_one("p.instock.availability")
        if not all((title_tag, price_tag, rating_tag, availability_tag)):
            LOGGER.warning("Skipping malformed book card in category %s", category)
            continue
        classes = [c for c in rating_tag.get("class", []) if c != "star-rating"]
        rating_text = classes[0] if classes else ""
        books.append(RawBook(
            title=title_tag.get("title") or title_tag.get_text(" ", strip=True),
            price=price_tag.get_text(" ", strip=True),
            star_rating=rating_text,
            availability=availability_tag.get_text(" ", strip=True),
            category=category,
        ))
    return books


def scrape_categories(category_urls: Iterable[str] = CATEGORY_URLS, min_rows: int = 60) -> list[RawBook]:
    """Scrape all listing pages for the selected categories.

    The site can have fewer than 20 books in a category, while other categories
    span multiple pages. Following each category's ``next`` link ensures the
    assignment minimum of 60 books is met without hard-coding page counts.
    """
    results: list[RawBook] = []
    visited: set[str] = set()

    for start_url in category_urls:
        url = start_url
        while url and url not in visited:
            visited.add(url)
            html = _fetch(url)
            soup = BeautifulSoup(html, "html.parser")
            category_tag = soup.select_one(".page-header h1")
            category = category_tag.get_text(" ", strip=True) if category_tag else start_url.rsplit('/', 2)[-2]
            results.extend(_parse_listing(html, category))

            next_link = soup.select_one("li.next a")
            url = urljoin(url, next_link.get("href")) if next_link and next_link.get("href") else ""

    if len(results) < min_rows:
        raise RuntimeError(f"Scrape returned {len(results)} books; minimum is {min_rows}.")
    if len({b.category for b in results}) < 3:
        raise RuntimeError("Scrape returned fewer than 3 categories.")
    return results
