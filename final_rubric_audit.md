# Final Rubric Audit

| Check | Status |
|---|---|
| required modules | YES |
| root readme | YES |
| fixed currency 105.50 | YES |
| 5 SQL queries | YES |
| exact support docs | YES |
| titanic csv | YES |
| EDA charts | YES |
| classifier metrics | YES |
| imbalance comparison | YES |
| RF tuning/OOB | YES |
| regression metrics | YES |
| final model comparison | YES |
| joblib pipeline | YES |
| reload validation | YES |
| dockerfile | YES |
| no root absolute paths | YES |

## Measured analytics evidence

| model               |   accuracy |   precision |   recall |       f1 |      auc |
|:--------------------|-----------:|------------:|---------:|---------:|---------:|
| Logistic Regression |   0.780899 |    0.754386 | 0.632353 | 0.688    | 0.826471 |
| Decision Tree       |   0.814607 |    0.786885 | 0.705882 | 0.744186 | 0.820655 |
| Random Forest       |   0.803371 |    0.779661 | 0.676471 | 0.724409 | 0.823195 |

## Regression

|     MAE |    RMSE |       R2 |   Adjusted_R2 |
|--------:|--------:|---------:|--------------:|
| 21.0986 | 41.7021 | 0.348163 |       0.30913 |

## Notes

Live BooksToScrape scraping, MiniLM/ChromaDB indexing, API transcript generation, and Docker build were not executed in this environment because network/Docker/optional package capabilities were unavailable. Those items are implemented and documented, but no fabricated outputs are included.
