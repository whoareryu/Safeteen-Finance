from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.gird_oracle_database_manager import get_db
from community.adapter.outbound.repositories.telegram_repository import TelegramRepository
from community.app.ports.input.telegram_use_case import TelegramUseCase
from community.app.ports.output.telegram_port import TelegramPort
from community.app.use_cases.telegram_interactor import TelegramInteractor


def get_telegram_repository(db: AsyncSession = Depends(get_db)) -> TelegramPort:
    return TelegramRepository(session=db)


def get_telegram_use_case(
    repository: TelegramPort = Depends(get_telegram_repository),
) -> TelegramUseCase:
    return TelegramInteractor(repository=repository)
