from pydantic import BaseModel


class WatcherRequest(BaseModel):
    id: int
    name: str


class WatcherResponse(BaseModel):
    id: int
    name: str


class ClassifyRequest(BaseModel):
    text: str


class ClassifyResponse(BaseModel):
    violates: bool
    score: float
    matched: list[str]
    categories: list[str]
    tokens: list[str]
