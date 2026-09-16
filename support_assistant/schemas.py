from __future__ import annotations
from pydantic import BaseModel, Field, field_validator

class AskRequest(BaseModel):
    query: str = Field(min_length=1)

class AnswerResponse(BaseModel):
    answer: str
    sources: list[str]
    confidence: float = Field(ge=0, le=1)
    @field_validator("sources")
    @classmethod
    def validate_sources(cls,v): return [str(x) for x in v]
