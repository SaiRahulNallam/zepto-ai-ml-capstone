# Data Pipeline

This module scrapes `books.toscrape.com` with `requests` + `BeautifulSoup`, cleans the scraped fields, applies the project-fixed `1 GBP = 105.50 INR` conversion, stores the result in normalized SQLite tables, and validates SQL/pandas equivalence.

## Run

From the repository root:

```bash
python -m data_pipeline.src.pipeline
```

The live scrape requires network access. The implementation fails loudly if the required site cannot be reached rather than fabricating data.

## Design decisions

- Scope: three book categories.
- Numeric parse failures use median imputation, as required.
- Unparseable availability rows are dropped and logged because a stock status cannot be safely inferred.
- `categories(category_id)` is the parent table and `books(category_id)` is the foreign key.
- Query outputs are written to `sql/query_outputs.md` after execution.
- `pd.read_sql_query` is used for SQL read-back; `pd.merge` independently reproduces the join.
