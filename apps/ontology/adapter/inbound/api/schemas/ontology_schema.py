from pydantic import BaseModel


class GraphQueryRequest(BaseModel):
    cypher: str
    params: dict = {}


class GraphQueryResponse(BaseModel):
    records: list[dict]


class ContextSearchRequest(BaseModel):
    query: str
    collection: str = "knowledge"
    limit: int = 5


class ContextSearchResponse(BaseModel):
    hits: list[dict]


class TopologyQueryRequest(BaseModel):
    question: str


class TopologyQueryResponse(BaseModel):
    answer: str
    source: str
    context: list[dict]


class DispatchRequest(BaseModel):
    task: str
    payload: dict = {}


class DispatchResponse(BaseModel):
    task_type: str
    routed_to: str
    result: dict
