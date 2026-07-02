from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.gird_oracle_database_manager import get_db
from chef.adapter.outbound.guardrail.kc_electra_guardrail import get_kc_electra_guardrail
from chef.adapter.outbound.repositories.receiver_repository import ReceiverRepository
from chef.app.ports.input.receiver_use_case import ReceiverUseCase
from chef.app.use_cases.receiver_interactor import ReceiverInteractor


def get_receiver_use_case(
    db: AsyncSession = Depends(get_db),
) -> ReceiverUseCase:
    return ReceiverInteractor(
        repository=ReceiverRepository(session=db),
        guardrail=get_kc_electra_guardrail(),
    )
