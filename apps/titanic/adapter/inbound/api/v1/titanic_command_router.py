import logging
from functools import lru_cache

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.database import get_sync_db
from apps.titanic.app.use_cases.titanic_schemas import ChatRequest
from apps.titanic.app.use_cases.titanic_command_impl import TitanicCommandUseCase

logger = logging.getLogger(__name__)

router = APIRouter(tags=["titanic-command"])


@lru_cache
def get_titanic_command_use_case() -> TitanicCommandUseCase:
    return TitanicCommandUseCase()


@router.post("/chat")
def titanic_chat(
    body: ChatRequest,
    db: Session = Depends(get_sync_db),
    use_case: TitanicCommandUseCase = Depends(get_titanic_command_use_case),
):
    """``titanic_passengers`` 테이블 컨텍스트로 Gemini 응답."""
    return use_case.chat(body, db)
