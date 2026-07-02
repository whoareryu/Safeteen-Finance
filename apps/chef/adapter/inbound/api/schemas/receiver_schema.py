from pydantic import BaseModel, Field


class ReceiverRequest(BaseModel):
    model_config = {"populate_by_name": True}

    sender: str = Field(alias="from", default="")
    subject: str = ""
    to: str = ""
    preview: str = ""
    message_id: str = Field(alias="messageId", default="")


class ReceiverResponse(BaseModel):
    status: str = "received"
