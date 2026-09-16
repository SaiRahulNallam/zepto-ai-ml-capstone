from __future__ import annotations
from pathlib import Path
from fastapi import FastAPI
from .graph import build_graph
from .schemas import AskRequest, AnswerResponse

app=FastAPI(title="Zepto Support Assistant",version="1.0.0")
_graph=None

def get_graph():
    global _graph
    if _graph is None: _graph=build_graph()
    return _graph

@app.get("/health")
def health(): return {"status":"ok"}

@app.post("/ask",response_model=AnswerResponse)
def ask(request:AskRequest):
    state=get_graph().invoke({"query":request.query})
    return AnswerResponse.model_validate(state["response"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("support_assistant.main:app",host="0.0.0.0",port=7860,reload=False)
