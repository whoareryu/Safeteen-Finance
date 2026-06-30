from pydantic import BaseModel


class SpamClassifyRequest(BaseModel):
    subject: str
    body: str
    sender: str | None = None


class SpamClassifyResponse(BaseModel):
    category: str
    label: str
    confidence: float
    is_spam: bool
    reason: str
