# Requirement-to-Implementation Matrix

| ID | Module | Requirement | Primary file(s) | Validation |
|---|---|---|---|---|
| DP-01 | data_pipeline | requests + BeautifulSoup, 3 categories, >=60 books | `src/scraper.py` | runtime guard + tests |
| DP-02 | data_pipeline | typed cleaning + fixed 105.50 conversion | `src/cleaner.py` | pytest |
| DP-03 | data_pipeline | normalized SQLite PK/FK | `src/database.py` | SQLite pragma/test |
| DP-04 | data_pipeline | 5 SQL queries + JOIN + outputs | `src/queries.py`, `sql/queries.sql` | live execution |
| DP-05 | data_pipeline | read_sql + merge equivalence | `src/queries.py` | `pandas_join_equivalence` |
| AN-01 | analytics | one Titanic load + CSV fallback | `src/pipeline.py` | code + CSV |
| AN-02 | analytics | profile/missing/IQR/skewness/bivariate/correlation/charts | `src/pipeline.py`, `01_eda.ipynb` | generated artifacts |
| AN-03 | analytics | stratified split + train-only preprocessing | `src/pipeline.py` | code/tests |
| AN-04 | analytics | 3 classifiers + metric suite + tree | `src/pipeline.py`, `02_modeling.ipynb` | generated artifacts |
| AN-05 | analytics | imbalance, SMOTE training-only | `src/pipeline.py` | generated artifact |
| AN-06 | analytics | RF GridSearchCV + OOB | `src/pipeline.py` | generated artifact |
| AN-07 | analytics | fare regression + residual analysis | `src/pipeline.py` | generated artifact |
| AN-08 | analytics | complete joblib pipeline + reload | `src/pipeline.py` | `reload_validation.json` |
| SA-01 | support_assistant | exact 8-document corpus | `docs/doc_01..08.txt` | file-count test |
| SA-02 | support_assistant | MiniLM + ChromaDB | `embeddings.py`, `retrieval.py` | local index build |
| SA-03 | support_assistant | structured prompt | `prompts.py` | source inspection |
| SA-04 | support_assistant | LangGraph 3 nodes + conditional edge | `graph.py` | unit/API run |
| SA-05 | support_assistant | MOCK_LLM deterministic baseline | `config.py`, `graph.py` | unit/API run |
| SA-06 | support_assistant | Pydantic /ask | `schemas.py`, `main.py` | API run |
| SA-07 | support_assistant | Dockerfile | `Dockerfile` | docker build/run |
| DOC-01 | repository | root/module READMEs | `README.md`, module READMEs | structure test |
| GIT-01 | repository | feature branch, 2 commits, merge | Git history | `git log --graph --all` |
