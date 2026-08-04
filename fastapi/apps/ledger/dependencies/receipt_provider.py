from __future__ import annotations

from typing import Callable

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.database import get_db
from ontology.app.ports.output.image_storage_gateway import ImageStorageGateway

from ledger.adapter.outbound.pg.receipt_pg_repository import ReceiptPgRepository
from ledger.app.ports.input.receipt_use_case import ReceiptUseCase
from ledger.app.ports.output.receipt_vision_parser_port import ReceiptVisionParserPort
from ledger.app.use_cases.receipt_interactor import ReceiptInteractor

# composition root(main.py)에서 등록하는 팩토리 — ontology 허브의 S3 어댑터와
# Gemini Vision 어댑터를 ledger 전용 설정으로 주입한다.
_image_storage_factory: Callable[[], ImageStorageGateway] | None = None
_vision_parser_factory: Callable[[], ReceiptVisionParserPort] | None = None


def register_image_storage_factory(factory: Callable[[], ImageStorageGateway]) -> None:
    global _image_storage_factory
    _image_storage_factory = factory


def register_vision_parser_factory(factory: Callable[[], ReceiptVisionParserPort]) -> None:
    global _vision_parser_factory
    _vision_parser_factory = factory


def _get_image_storage_gateway() -> ImageStorageGateway:
    if _image_storage_factory is None:
        raise RuntimeError("image storage factory가 등록되지 않았습니다 (main.py composition root 확인)")
    return _image_storage_factory()


def _get_vision_parser() -> ReceiptVisionParserPort:
    if _vision_parser_factory is None:
        raise RuntimeError("vision parser factory가 등록되지 않았습니다 (main.py composition root 확인)")
    return _vision_parser_factory()


def get_receipt_use_case(db: AsyncSession = Depends(get_db)) -> ReceiptUseCase:
    return ReceiptInteractor(
        receipt_repository=ReceiptPgRepository(session=db),
        vision_parser=_get_vision_parser(),
        storage=_get_image_storage_gateway(),
    )
