# Zepto Data & AI Platform

A single capstone repository containing three linked engineering capabilities: a scraping-to-SQL data pipeline, a Titanic analytics/modeling pipeline, and an offline-first RAG support assistant. The capstone requires exactly one repository containing `data_pipeline`, `analytics`, and `support_assistant`, with setup/run guidance and design decisions documented here. fileciteturn1file0L24-L37

## Repository Structure

```text
zepto-ai-ml-capstone/
├── README.md
├── requirements.txt
├── .gitignore
├── data_pipeline/
├── analytics/
├── support_assistant/
└── tests/
```

## Technology Stack

Python 3.11; requests; BeautifulSoup; pandas; SQLite; seaborn/matplotlib; scikit-learn; imbalanced-learn; joblib; sentence-transformers (`all-MiniLM-L6-v2`); ChromaDB; LangGraph; Pydantic; FastAPI; Uvicorn; Docker.

## Setup

A single root `requirements.txt` is used for all three modules.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The support assistant defaults to `MOCK_LLM=1`, requiring no LLM API key. The project specification describes this offline mock path as the graded baseline; the real-LLM path is optional. fileciteturn1file0L24-L47

## Module 1 — Data Pipeline

Architecture: `books.toscrape.com → raw HTML → BeautifulSoup extraction → typed cleaning → GBP→INR fixed conversion (105.50) → normalized SQLite → SQL queries → pandas read-back/merge equivalence`.

Run:

```bash
python -m data_pipeline.src.pipeline
pytest -q data_pipeline/tests
```

The scraper uses three categories, requires at least 60 books, and captures title, price, star rating, availability, and category. The project-defined rate is exactly `1 GBP = 105.50 INR`; it is not a live exchange rate. fileciteturn0file1L70-L100

## Module 2 — Analytics

The loader calls `sns.load_dataset('titanic')` once, immediately writes `analytics/titanic.csv`, and subsequent modeling reads the committed CSV. This matches the requirement that the raw dataset is loaded once and then reused. fileciteturn1file0L145-L164

Run:

```bash
python -m analytics.src.pipeline
pytest -q analytics/tests
```

Artifacts are written to `analytics/outputs/` and the complete fitted preprocessing + estimator is saved as `analytics/models/best_pipeline.joblib`. The model pipeline is raw-input compatible after reload. fileciteturn1file0L250-L264

## Module 3 — Support Assistant

Pipeline: `docs/*.txt → chunking → all-MiniLM-L6-v2 embeddings → ChromaDB(zepto_policy) → LangGraph classify_intent → conditional retrieval/direct path → deterministic MOCK_LLM response → Pydantic → FastAPI /ask`.

Build index:

```bash
python -m support_assistant.build_index
```

Run API:

```bash
MOCK_LLM=1 uvicorn support_assistant.main:app --host 0.0.0.0 --port 7860
```

Example calls:

```bash
curl -X POST http://localhost:7860/ask -H "Content-Type: application/json" -d '{"query":"What is the delivery fee for an order below INR 149?"}'
curl -X POST http://localhost:7860/ask -H "Content-Type: application/json" -d '{"query":"What is the capital of France?"}'
```

The eight supplied policy documents are stored verbatim in `support_assistant/docs/`. The mock classifier uses the required keyword heuristic; policy queries retrieve top-3 cosine-similarity chunks, while general questions return the fixed policy-focused mock response. fileciteturn1file0L49-L67 fileciteturn1file0L117-L154

### Docker

```bash
cd support_assistant
docker build -t zepto-support-assistant .
docker run --rm -p 7860:7860 zepto-support-assistant
```

The Dockerfile is the required local container baseline; cloud deployment is optional. fileciteturn1file0L155-L171

## Validation / Acceptance Coverage

| Requirement | Implementation | Evidence |
|---|---|---|
| 60+ books / 3 categories | `data_pipeline/src/scraper.py` | Runtime validation in `pipeline.py` |
| Typed cleaning + 105.50 rate | `cleaner.py` | `test_data_pipeline.py` |
| PK/FK SQLite | `database.py` | SQLite + pytest |
| 5+ SQL + JOIN | `queries.py`, `sql/queries.sql` | output capture after live run |
| `pd.read_sql` + `pd.merge` equivalence | `queries.py` | `pandas_join_equivalence()` |
| Titanic load once + CSV fallback | `analytics/src/pipeline.py` | `titanic.csv`, tests |
| EDA requirements | `pipeline.py`, `01_eda.ipynb` | `analytics/outputs/` |
| Three classifiers + full metrics | `pipeline.py`, `02_modeling.ipynb` | metrics + plots |
| Imbalance / SMOTE / GridSearchCV / OOB | `pipeline.py` | tuning + imbalance outputs |
| Regression metrics + residuals | `pipeline.py` | regression outputs |
| Saved complete joblib pipeline | `analytics/models/best_pipeline.joblib` | reload validation |
| 8 exact policy docs | `support_assistant/docs/` | file-count test |
| MiniLM + ChromaDB | `embeddings.py`, `retrieval.py` | `build_index.py` |
| LangGraph 3-node conditional graph | `graph.py` | core tests + API run |
| MOCK_LLM baseline | `graph.py`, `.env.example` | deterministic branch |
| Pydantic + FastAPI `/ask` | `schemas.py`, `main.py` | API examples |
| Docker | `support_assistant/Dockerfile` | local docker build/run |
| Git feature branch / 2 commits / merge | repository history | `git log --graph --all` |

## Git workflow

The capstone requires a feature branch created from `main`, at least two commits on that branch, and a merge back into `main`. fileciteturn0file1L50-L58

Example workflow for your own Git host:

```bash
git checkout -b feature/capstone-implementation
git add . && git commit -m "feat: implement capstone modules"
# make a second meaningful commit
git add . && git commit -m "test: add validation and documentation"
git checkout main
git merge --no-ff feature/capstone-implementation -m "merge: capstone implementation"
git log --graph --oneline --all
```

Do not manufacture timestamps or deceptive history; the final history should show genuine branch/commit/merge activity. fileciteturn0file0L911-L932

## Important execution note for this build environment

This repository was generated in an environment without outbound DNS/network access, without Docker, and without the optional Support Assistant packages preinstalled. I therefore did **not** fabricate the scraper outputs, ChromaDB vectors, API JSON transcripts, or Docker build evidence. The code and tests are present, and the commands that require those unavailable capabilities are documented as local execution steps. The same principle is applied to analytics: where `sns.load_dataset('titanic')` cannot reach the network/cache in this environment, the committed `analytics/titanic.csv` is used solely as the offline fallback required by the capstone.
