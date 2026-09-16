from pathlib import Path
from support_assistant.graph import classify_intent, direct_answer
from support_assistant.retrieval import chunk_documents
from support_assistant.schemas import AnswerResponse

def test_exactly_eight_docs():
    docs=Path(__file__).resolve().parents[1]/"docs"; chunks=chunk_documents(docs); assert len({c.document_id for c in chunks})==8

def test_keyword_routing_and_mock_general():
    assert classify_intent({"query":"delivery fee"})["intent"]=="policy_question"
    assert classify_intent({"query":"capital of France"})["intent"]=="general_question"
    out=direct_answer({"query":"capital"})["response"]; AnswerResponse.model_validate(out); assert out["sources"]==[]
