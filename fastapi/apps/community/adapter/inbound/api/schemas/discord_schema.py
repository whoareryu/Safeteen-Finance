from pydantic import BaseModel, Field


class DiscordSchema(BaseModel):
    id: int = Field(2, description="Bot ID")
    name: str = Field("Chef Discord Bot", description="Bot name")

    model_config = {
        "json_schema_extra": {"example": {"id": 2, "name": "Chef Discord Bot"}}
    }


class DiscordWebhookRequest(BaseModel):
    channel_id: str
    username: str
    content: str


class DiscordWebhookResponse(BaseModel):
    channel_id: str
    bot_reply: str
