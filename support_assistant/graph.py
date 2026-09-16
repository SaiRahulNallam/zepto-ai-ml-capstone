from __future__ import annotations
from typing import TypedDict, Literal
import json
from .config import MOCK_LLM, GROQ_API_KEY, GROQ_MODEL
from .prompts import build_prompt
from .retrieval import retrieve
from .schemas import AnswerResponse

KEYWORDS=("delivery","return","refund","membership","tracking","cancel","gift card","support hours")

class GraphState(TypedDict, total=False):
    query:str
    intent:Literal["policy_question","general_question"]
    retrieved:list[dict]
    response:dict


def _real_intent(query:str)->str:
    if not GROQ_API_KEY: raise RuntimeError("MOCK_LLM=0 requires GROQ_API_KEY.")
    from groq import Groq
    client=Groq(api_key=GROQ_API_KEY)
    last_error=None
    for attempt in range(3):
        try:
            instruction=("Classify the query as exactly one token: policy_question or general_question. "
                         "Use policy_question only for questions about the supplied Zepto policy corpus. Return only the token.")
            if attempt: instruction += " Correct any previous formatting mistake and return only one of the two allowed tokens."
            raw=client.chat.completions.create(model=GROQ_MODEL,messages=[{"role":"user","content":instruction+"\nQuery: "+query}],temperature=0).choices[0].message.content.strip()
            if raw in {"policy_question","general_question"}: return raw
            last_error=ValueError(f"Invalid intent: {raw}")
        except Exception as exc: last_error=exc
    raise RuntimeError(f"Could not obtain a valid real-LLM intent after 3 attempts: {last_error}")


def classify_intent(state:GraphState)->GraphState:
    q=state["query"].lower()
    if MOCK_LLM:
        intent="policy_question" if any(k in q for k in KEYWORDS) else "general_question"
    else:
        intent=_real_intent(state["query"])
    return {**state,"intent":intent}


def _real_llm(prompt:str)->dict:
    if not GROQ_API_KEY: raise RuntimeError("MOCK_LLM=0 requires GROQ_API_KEY.")
    from groq import Groq
    client=Groq(api_key=GROQ_API_KEY)
    last_error=None
    for attempt in range(3):
        try:
            suffix="\nReturn ONLY valid JSON with answer, sources, confidence." if attempt==0 else "\nCorrect your previous response. Return ONLY JSON matching answer:string, sources:list[string], confidence:number between 0 and 1."
            raw=client.chat.completions.create(model=GROQ_MODEL,messages=[{"role":"user","content":prompt+suffix}],temperature=0).choices[0].message.content
            return AnswerResponse.model_validate_json(raw).model_dump()
        except Exception as exc: last_error=exc
    return AnswerResponse(answer=f"LLM structured-output error after 3 attempts: {last_error}",sources=[],confidence=0.0).model_dump()


def retrieve_and_answer(state:GraphState)->GraphState:
    retrieved=retrieve(state["query"],top_k=3)
    top_snippet=retrieved[0]["text"][:200]
    if MOCK_LLM:
        response=AnswerResponse(answer=f"Based on the retrieved context: {top_snippet}",sources=[r["metadata"]["chunk_id"] for r in retrieved],confidence=1.0).model_dump()
    else:
        context="\n\n".join(r["text"] for r in retrieved); response=_real_llm(build_prompt(state["query"],context))
    return {**state,"retrieved":retrieved,"response":response}


def direct_answer(state:GraphState)->GraphState:
    if MOCK_LLM:
        response=AnswerResponse(answer="I can only answer questions about Zepto policies right now.",sources=[],confidence=1.0).model_dump()
    else:
        response=_real_llm(build_prompt(state["query"],""))
    return {**state,"response":response}


def _route(state:GraphState): return "retrieve_and_answer" if state["intent"]=="policy_question" else "direct_answer"


def build_graph():
    from langgraph.graph import StateGraph, START, END
    g=StateGraph(GraphState)
    g.add_node("classify_intent",classify_intent); g.add_node("retrieve_and_answer",retrieve_and_answer); g.add_node("direct_answer",direct_answer)
    g.add_edge(START,"classify_intent"); g.add_conditional_edges("classify_intent",_route,{"retrieve_and_answer":"retrieve_and_answer","direct_answer":"direct_answer"}); g.add_edge("retrieve_and_answer",END); g.add_edge("direct_answer",END)
    return g.compile()
