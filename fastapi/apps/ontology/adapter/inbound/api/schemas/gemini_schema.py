from pydantic import BaseModel


class GeminiQueryRequest(BaseModel):
    question: str


class GeminiQueryResponse(BaseModel):
    answer: str
