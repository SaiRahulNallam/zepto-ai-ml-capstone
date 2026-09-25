# Support Assistant

Offline-first RAG service using the exact eight policy documents from the capstone. The graded baseline is `MOCK_LLM=1` (default): intent classification is keyword-based, embeddings/retrieval are local, and answer generation is deterministic.

## Index

```bash
python -m support_assistant.build_index
```

This uses `sentence-transformers` with `all-MiniLM-L6-v2` and stores vectors in the ChromaDB collection `zepto_policy`.

## Run API

```bash
uvicorn support_assistant.main:app --host 0.0.0.0 --port 7860
```

## Examples

### Example 1 — Policy Question

### Request:

```json
{
  "query": "What are the customer support hours?"
}
```

### Actual Response

```json
{"answer":"Based on the retrieved context: Zepto customer support is available via in-app chat 24 hours a day, 7 days a week, given the time-sensitive nature of quick commerce deliveries. Average in-app chat response time is under 2 minutes. E","sources":["doc_08_chunk_0","doc_06_chunk_0","doc_02_chunk_0"],"confidence":1.0}
```

### Example 2 — General Question

### Request:

```json
{
  "query": "Who is the CEO of Zepto?"
}
```

### Actual Response

```json
{"answer":"I can only answer questions about Zepto policies right now.","sources":[],"confidence":1.0}
```

The actual API JSON responses are recorded in `support_assistant/examples/responses.md`.

## Architecture

INGESTION (`docs/*.txt`) → CHUNKING (`retrieval.chunk_documents`) → EMBEDDING (`embeddings.py`, `all-MiniLM-L6-v2`) → CHROMADB (`zepto_policy`) → RETRIEVAL (`retrieve_and_answer`, cosine top-3) → GENERATION (`retrieve_and_answer` mock template or optional real LLM using `prompts.py`) → PYDANTIC VALIDATION (`schemas.py`) → FASTAPI (`main.py`, `/ask`). The `classify_intent` node always uses the required keyword-based routing heuristic. `MOCK_LLM` controls answer generation: mock mode uses deterministic responses, while `MOCK_LLM=0` enables the optional Groq-backed generation path. Retrieval for policy questions always runs locally.

## Results

Validated locally with `MOCK_LLM=1`:

- ChromaDB collection: `zepto_policy`
- Indexed policy documents/chunks: 8
- Policy `/ask` test: passed
- Policy response sources: 3
- Policy response confidence: 1.0
- General `/ask` test: passed
- General response sources: []
- General response confidence: 1.0
- Docker image build: passed
- Docker container startup: passed
- Docker `GET /health`: `{"status":"ok"}`
- Docker `/ask` policy test: passed
- Docker `/ask` general test: passed