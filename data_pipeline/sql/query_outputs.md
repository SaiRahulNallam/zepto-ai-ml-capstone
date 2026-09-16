# SQL Query Execution Status

The live BooksToScrape crawl could not be executed in the build environment because outbound DNS/network access was unavailable. `queries.py` contains all five required SQL statements and writes their real outputs when `python -m data_pipeline.src.pipeline` is run on a network-enabled environment. No SQL output values are fabricated here.
