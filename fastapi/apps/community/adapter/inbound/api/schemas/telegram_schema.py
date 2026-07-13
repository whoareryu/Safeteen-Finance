from pydantic import BaseModel, Field


class TelegramSchema(BaseModel):
    id: int = Field(1, description="Bot ID")
    name: str = Field("Chef Telegram Bot", description="Bot name")

    model_config = {
        "json_schema_extra": {"example": {"id": 1, "name": "Chef Telegram Bot"}}
    }


class TelegramHistoryItem(BaseModel):
    text: str
    sent_at: str


class TelegramHistoryResponse(BaseModel):
    items: list[TelegramHistoryItem]
