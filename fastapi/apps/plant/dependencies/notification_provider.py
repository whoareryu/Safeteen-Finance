from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.database import get_db
from core.matrix.secret_manager import secret_manager

from plant.adapter.outbound.coupang.coupang_search_link_adapter import CoupangSearchLinkAdapter
from plant.adapter.outbound.n8n.channel_strategies.discord_channel_strategy import (
    DiscordChannelStrategy,
)
from plant.adapter.outbound.n8n.channel_strategies.kakao_channel_strategy import (
    KakaoChannelStrategy,
)
from plant.adapter.outbound.n8n.channel_strategies.telegram_channel_strategy import (
    TelegramChannelStrategy,
)
from plant.adapter.outbound.n8n.n8n_notification_gateway import N8nNotificationGateway
from plant.adapter.outbound.pg.care_schedule_pg_repository import CareSchedulePgRepository
from plant.adapter.outbound.pg.notification_pg_repository import NotificationPgRepository
from plant.app.ports.input.notification_use_case import NotificationUseCase
from plant.app.ports.output.notification_repository import NotificationRepository
from plant.app.use_cases.notification_interactor import NotificationInteractor

_HUB_URL = secret_manager.get_secret("N8N_HUB_WEBHOOK_URL", "")
_COUPANG_LINK = CoupangSearchLinkAdapter()
_GATEWAY = N8nNotificationGateway(
    strategies={
        "kakao": KakaoChannelStrategy(webhook_url=_HUB_URL),
        "discord": DiscordChannelStrategy(webhook_url=_HUB_URL),
        "telegram": TelegramChannelStrategy(webhook_url=_HUB_URL),
    }
)


def get_notification_repository(db: AsyncSession = Depends(get_db)) -> NotificationRepository:
    return NotificationPgRepository(session=db)


def get_notification_use_case(db: AsyncSession = Depends(get_db)) -> NotificationUseCase:
    return NotificationInteractor(
        care_schedule_repository=CareSchedulePgRepository(session=db),
        notification_repository=NotificationPgRepository(session=db),
        gateway=_GATEWAY,
        coupang_link=_COUPANG_LINK,
    )
