from pydantic import BaseModel, EmailStr, Field


class EmailSendRequest(BaseModel):
    to: EmailStr
    prompt: str


class EmailSendResponse(BaseModel):
    to: str
    subject: str
    body: str
    status: str = "sent"


class EmailReceiveRequest(BaseModel):
    model_config = {"populate_by_name": True}

    sender: str = Field(alias="from", default="")
    subject: str = ""
    to: str = ""
    preview: str = ""
    message_id: str = Field(alias="messageId", default="")


class EmailReceiveResponse(BaseModel):
    status: str = "received"
