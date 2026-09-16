from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT=Path(__file__).resolve().parent
load_dotenv(ROOT/".env")
MOCK_LLM=os.getenv("MOCK_LLM","1") != "0"
CHROMA_PATH=Path(os.getenv("CHROMA_PATH", str(ROOT/"chroma_db")))
COLLECTION_NAME=os.getenv("CHROMA_COLLECTION","zepto_policy")
EMBEDDING_MODEL=os.getenv("EMBEDDING_MODEL","all-MiniLM-L6-v2")
GROQ_API_KEY=os.getenv("GROQ_API_KEY")
GROQ_MODEL=os.getenv("GROQ_MODEL","llama-3.1-8b-instant")
