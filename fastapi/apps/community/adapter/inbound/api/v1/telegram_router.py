from __future__ import annotations

from fastapi import APIRouter, Depends

from apps.auth.dependencies import require_owner
from community.adapter.inbound.api.schemas.telegram_schema import (
    TelegramHistoryItem,
    TelegramSchema,
    TelegramSendRequest,
)
from community.app.dtos.telegram_dto import TelegramQuery
from community.app.ports.input.telegram_use_case import TelegramUseCase
from community.dependencies.telegram_provider import get_telegram_use_case

telegram_router = APIRouter(prefix="/telegram", tags=["chef-telegram"])


@telegram_router.get("/myself")
async def introduce_myself(
    use_case: TelegramUseCase = Depends(get_telegram_use_case),
) -> dict:
    result = await use_case.introduce_myself(TelegramQuery(id=1, name="Chef Telegram Bot"))
    return {"id": result.id, "name": result.name}


@telegram_router.post(
    "/send", response_model=TelegramHistoryItem, dependencies=[Depends(require_owner)]
)
async def send_message(
    body: TelegramSendRequest,
    use_case: TelegramUseCase = Depends(get_telegram_use_case),
) -> TelegramHistoryItem:
    result = await use_case.send(body.text)
    return TelegramHistoryItem(text=result.text, sent_at=result.sent_at.isoformat())


@telegram_router.get(
    "/history", response_model=list[TelegramHistoryItem], dependencies=[Depends(require_owner)]
)
async def get_history(
    use_case: TelegramUseCase = Depends(get_telegram_use_case),
) -> list[TelegramHistoryItem]:
    messages = await use_case.list_history(limit=100)
    return [TelegramHistoryItem(text=m.text, sent_at=m.sent_at.isoformat()) for m in messages]
