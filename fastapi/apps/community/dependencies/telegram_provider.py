import os

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.gird_oracle_database_manager import get_db
from community.adapter.outbound.repositories.telegram_repository import TelegramRepository
from community.adapter.outbound.telegram.telegram_bot_gateway import TelegramBotGateway
from community.app.ports.input.telegram_use_case import TelegramUseCase
from community.app.ports.output.telegram_gateway import TelegramGateway
from community.app.ports.output.telegram_port import TelegramPort
from community.app.use_cases.telegram_interactor import TelegramInteractor


def get_telegram_repository(db: AsyncSession = Depends(get_db)) -> TelegramPort:
    return TelegramRepository(session=db)


def get_telegram_gateway() -> TelegramGateway:
    return TelegramBotGateway(
        bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
    )


def get_telegram_use_case(
    repository: TelegramPort = Depends(get_telegram_repository),
    gateway: TelegramGateway = Depends(get_telegram_gateway),
) -> TelegramUseCase:
    return TelegramInteractor(repository=repository, gateway=gateway)
