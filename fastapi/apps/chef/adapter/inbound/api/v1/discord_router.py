from fastapi import APIRouter, Depends

from chef.adapter.inbound.api.schemas.discord_schema import (
    DiscordSchema,
    DiscordWebhookRequest,
    DiscordWebhookResponse,
)
from chef.app.dtos.discord_dto import DiscordMessageCommand, DiscordQuery
from chef.app.ports.input.discord_use_case import DiscordUseCase
from chef.dependencies.discord_provider import get_discord_use_case

"""
Chef Discord Bot
디스코드 웹훅 수신 및 봇 자기소개 라우터
"""

discord_router = APIRouter(prefix="/discord", tags=["chef-discord"])


@discord_router.get("/myself")
async def introduce_myself(
    use_case: DiscordUseCase = Depends(get_discord_use_case),
) -> dict:
    result = await use_case.introduce_myself(DiscordQuery(id=2, name="Chef Discord Bot"))
    return {"id": result.id, "name": result.name}


@discord_router.post("/webhook", response_model=DiscordWebhookResponse)
async def receive_webhook(
    body: DiscordWebhookRequest,
    use_case: DiscordUseCase = Depends(get_discord_use_case),
) -> DiscordWebhookResponse:
    result = await use_case.receive_message(
        DiscordMessageCommand(
            channel_id=body.channel_id,
            username=body.username,
            content=body.content,
        )
    )
    return DiscordWebhookResponse(channel_id=result.channel_id, bot_reply=result.bot_reply)
