# Zepto Data & AI Platform

A single capstone repository containing three linked engineering capabilities: a scraping-to-SQL data pipeline, a Titanic analytics/modeling pipeline, and an offline-first RAG support assistant. The capstone requires exactly one repository containing `data_pipeline`, `analytics`, and `support_assistant`, with setup/run guidance and design decisions documented here.

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

Python 3.11 is the tested project environment. The Support Assistant was validated using Python 3.11.9.
A single root `requirements.txt` is used for all three modules.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The support assistant defaults to `MOCK_LLM=1`, requiring no LLM API key. The project specification describes this offline mock path as the graded baseline; the real-LLM path is optional.

## Module 1 — Data Pipeline

Architecture: `books.toscrape.com → raw HTML → BeautifulSoup extraction → typed cleaning → GBP→INR fixed conversion (105.50) → normalized SQLite → SQL queries → pandas read-back/merge equivalence`.

Run:

```bash
python -m data_pipeline.src.pipeline
pytest -q data_pipeline/tests
```

The scraper uses three categories, requires at least 60 books, and captures title, price, star rating, availability, and category. The project-defined rate is exactly `1 GBP = 105.50 INR`; it is not a live exchange rate.

## Module 2 — Analytics

The loader calls `sns.load_dataset('titanic')` once, immediately writes `analytics/titanic.csv`, and subsequent modeling reads the committed CSV. This matches the requirement that the raw dataset is loaded once and then reused.

Run:

```bash
python -m analytics.src.pipeline
pytest -q analytics/tests
```

Artifacts are written to `analytics/outputs/` and the complete fitted preprocessing + estimator is saved as `analytics/models/best_pipeline.joblib`. The model pipeline is raw-input compatible after reload.

## Module 3 — Support Assistant

Pipeline: `docs/*.txt → chunking → all-MiniLM-L6-v2 embeddings → ChromaDB(zepto_policy) → LangGraph classify_intent → conditional retrieval/direct path → deterministic MOCK_LLM response → Pydantic → FastAPI /ask`.

Build index:

```bash
python -m support_assistant.build_index
```

Run API:

```bash
uvicorn support_assistant.main:app --host 0.0.0.0 --port 7860
```

Example calls:

```bash
curl -X POST http://localhost:7860/ask -H "Content-Type: application/json" -d '{"query":"What is the delivery fee for an order below INR 149?"}'
curl -X POST http://localhost:7860/ask -H "Content-Type: application/json" -d '{"query":"What is the capital of France?"}'
```

The eight supplied policy documents are stored verbatim in `support_assistant/docs/`. The mock classifier uses the required keyword heuristic; policy queries retrieve top-3 cosine-similarity chunks, while general questions return the fixed policy-focused mock response.

### Docker

```bash
docker build -t zepto-support-assistant -f support_assistant/Dockerfile .
docker run --rm -p 7860:7860 zepto-support-assistant
```

The Dockerfile is the required local container baseline; cloud deployment is optional.

## Design Decisions

### Module 1 — Data Pipeline

- Used three book categories and a minimum 60-row scraping scope.
- Used the required fixed conversion rate of 1 GBP = 105.50 INR.
- Used normalized SQLite tables with a primary-key/foreign-key relationship.
- Used both SQL queries and pandas to validate the join result.

### Module 2 — Analytics

- Loaded the Titanic dataset once and committed `analytics/titanic.csv` as the offline fallback.
- Used a stratified train/test split before train-only preprocessing.
- Used a scikit-learn `ColumnTransformer` and `Pipeline` to keep preprocessing inside the training workflow.
- Compared three classifiers, imbalance strategies, Random Forest tuning, and the regression side-task.

### Module 3 — Support Assistant

- Used local `all-MiniLM-L6-v2` embeddings and ChromaDB for offline retrieval.
- Used LangGraph conditional routing between policy retrieval and direct-answer paths.
- Used `MOCK_LLM=1` as the deterministic graded baseline.
- Used Pydantic validation and FastAPI for the final structured API response.

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

The capstone requires a feature branch created from `main`, at least two commits on that branch, and a merge back into `main`.

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

Do not manufacture timestamps or deceptive history; the final history should show genuine branch/commit/merge activity.

## Execution Note

Some components of the project were developed in environments with limited network or package availability. Where external dependencies were unavailable during development, no execution results were fabricated.

The Support Assistant was subsequently validated locally with its required dependencies, including index building, FastAPI `/ask` requests, and Docker build/run. Actual API response evidence is recorded in `support_assistant/examples/responses.md`.

For Analytics, the committed `analytics/titanic.csv` supports the required offline fallback when `sns.load_dataset('titanic')` is unavailable.

## Local Docker Validation

The Support Assistant was validated locally with Docker on September 22, 2026.

- Docker image build: passed (`zepto-support-assistant`)
- Container startup: passed on port 7860
- `GET /health`: returned `status: ok`
- `POST /ask` policy question: returned `answer`, 3 retrieved sources, and `confidence: 1.0`
- `POST /ask` general question: returned the policy-focused response, `sources: []`, and `confidence: 1.0`
- Raw API responses are recorded in `support_assistant/examples/responses.md`
