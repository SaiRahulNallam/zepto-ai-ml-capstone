# Execution Evidence

Generated on 2026-09-16 in the provided execution environment.

## Environment checks

- Python 3.13.5 is available.
- Core analytics/data packages are installed.
- `langgraph`, `chromadb`, and `sentence_transformers` are not installed in the environment at build time.
- Docker CLI is not installed.
- DNS/network access to `books.toscrape.com` and Seaborn's online dataset repository is unavailable.

## What was actually executed

1. Repository generation and structure creation.
2. `python -m analytics.src.pipeline` completed and generated real EDA, classification, imbalance, tuning, regression, chart, and joblib artifacts from the committed offline Titanic fallback.
3. `python -m pytest -q` completed with 11 passing tests.
4. The Titanic raw network/cache load was attempted once and failed due unavailable DNS, after which the committed CSV fallback was used.

## What could not honestly be recorded here

The live BooksToScrape crawl, live ChromaDB/ MiniLM indexing, FastAPI integration run, and Docker build/run require capabilities absent from this environment. No output values were invented for those steps.

## Local commands to complete the evidence on a network-enabled Python 3.11 environment

```bash
pip install -r requirements.txt
python -m data_pipeline.src.pipeline
python -m analytics.src.pipeline
python -m support_assistant.build_index
MOCK_LLM=1 uvicorn support_assistant.main:app --host 0.0.0.0 --port 7860
python support_assistant/examples/run_examples.py
docker build -t zepto-support-assistant support_assistant
docker run --rm -p 7860:7860 zepto-support-assistant
pytest -q
```

The validation suite was rerun after the final rubric-audit changes.
