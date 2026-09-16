from __future__ import annotations
from .config import EMBEDDING_MODEL

_model=None

def get_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError("sentence-transformers is required for MiniLM embeddings. Install requirements.txt.") from exc
        _model=SentenceTransformer(EMBEDDING_MODEL)
    return _model

def embed_texts(texts:list[str]): return get_model().encode(texts, normalize_embeddings=True).tolist()

def embed_query(text:str): return get_model().encode([text], normalize_embeddings=True)[0].tolist()
