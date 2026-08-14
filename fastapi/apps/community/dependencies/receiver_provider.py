from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.infra.database_manager import get_db
from community.adapter.outbound.guardrail.kc_electra_guardrail import get_kc_electra_guardrail
from community.adapter.outbound.repositories.receiver_repository import ReceiverRepository
from community.app.ports.input.receiver_use_case import ReceiverUseCase
from community.app.use_cases.receiver_interactor import ReceiverInteractor


def get_receiver_use_case(
    db: AsyncSession = Depends(get_db),
) -> ReceiverUseCase:
    return ReceiverInteractor(
        repository=ReceiverRepository(session=db),
        guardrail=get_kc_electra_guardrail(),
    )
