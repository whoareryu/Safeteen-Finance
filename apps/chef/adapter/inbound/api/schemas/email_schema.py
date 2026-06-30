from pydantic import BaseModel, EmailStr


class EmailSendRequest(BaseModel):
    to: EmailStr
    prompt: str


class EmailSendResponse(BaseModel):
    to: str
    subject: str
    body: str
    status: str = "sent"
