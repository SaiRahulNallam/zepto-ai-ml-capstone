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

```bash
curl -X POST http://localhost:7860/ask -H "Content-Type: application/json" -d '{"query":"What is the delivery fee for an order below INR 149?"}'
curl -X POST http://localhost:7860/ask -H "Content-Type: application/json" -d '{"query":"What is the capital of France?"}'
```

Run `python support_assistant/examples/run_examples.py` after indexing to record actual JSON output into the root README before submission.

## Architecture

INGESTION (`docs/*.txt`) → CHUNKING (`retrieval.chunk_documents`) → EMBEDDING (`embeddings.py`, `all-MiniLM-L6-v2`) → CHROMADB (`zepto_policy`) → RETRIEVAL (`retrieve_and_answer`, cosine top-3) → GENERATION (`retrieve_and_answer` mock template or optional real LLM using `prompts.py`) → PYDANTIC VALIDATION (`schemas.py`) → FASTAPI (`main.py`, `/ask`). The `classify_intent`, `retrieve_and_answer`, and `direct_answer` nodes all branch on `MOCK_LLM`: mock mode uses deterministic keyword/template logic, while `MOCK_LLM=0` enables the optional Groq-backed classification/generation path. Retrieval itself always runs locally for policy questions.
