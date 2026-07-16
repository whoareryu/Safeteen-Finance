from pydantic import BaseModel, Field


class SemanticRoutingRequest(BaseModel):
    question: str


class SemanticRoutingResponse(BaseModel):
    answer: str
    destination: str
    entities: list[str] = Field(default_factory=list)
