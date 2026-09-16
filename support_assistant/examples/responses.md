# API Response Evidence

The raw API transcripts are intentionally not fabricated in this build environment because `sentence-transformers`, ChromaDB, and LangGraph were not installed and the environment had no network access for dependency installation. After installing `requirements.txt`, run `python -m support_assistant.build_index`, start FastAPI, and use the two JSON example files to record the actual responses here.
