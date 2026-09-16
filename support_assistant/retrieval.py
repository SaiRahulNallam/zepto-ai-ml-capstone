from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import math
import re
from typing import Iterable
from .config import CHROMA_PATH, COLLECTION_NAME
from .embeddings import embed_texts, embed_query

@dataclass(frozen=True)
class Chunk:
    document_id:str
    filename:str
    chunk_id:str
    text:str


def chunk_documents(docs_dir:Path, chunk_size:int=800) -> list[Chunk]:
    chunks=[]
    for path in sorted(docs_dir.glob("doc_*.txt")):
        text=path.read_text(encoding="utf-8")
        parts=[text[i:i+chunk_size] for i in range(0,len(text),chunk_size)] or [""]
        doc_id=path.stem
        for i,part in enumerate(parts): chunks.append(Chunk(doc_id,path.name,f"{doc_id}_chunk_{i}",part))
    if len({c.document_id for c in chunks}) != 8: raise ValueError("Exactly 8 policy documents are required.")
    return chunks


def build_collection(docs_dir:Path):
    import chromadb
    chunks=chunk_documents(docs_dir)
    client=chromadb.PersistentClient(path=str(CHROMA_PATH))
    try: client.delete_collection(COLLECTION_NAME)
    except Exception: pass
    collection=client.get_or_create_collection(name=COLLECTION_NAME, metadata={"hnsw:space":"cosine"})
    embeddings=embed_texts([c.text for c in chunks])
    collection.add(ids=[c.chunk_id for c in chunks],documents=[c.text for c in chunks],metadatas=[{"document_id":c.document_id,"filename":c.filename,"chunk_id":c.chunk_id} for c in chunks],embeddings=embeddings)
    return collection


def get_collection():
    import chromadb
    client=chromadb.PersistentClient(path=str(CHROMA_PATH))
    return client.get_or_create_collection(name=COLLECTION_NAME, metadata={"hnsw:space":"cosine"})


def retrieve(query:str, top_k:int=3):
    collection=get_collection(); emb=embed_query(query)
    result=collection.query(query_embeddings=[emb],n_results=top_k,include=["documents","metadatas","distances"])
    docs=result.get("documents", [[]])[0]; metas=result.get("metadatas", [[]])[0]; dists=result.get("distances", [[]])[0]
    return [{"text":d,"metadata":m,"distance":float(dist)} for d,m,dist in zip(docs,metas,dists)]
